import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .config import DEFAULT_CONCURRENCY, PER_MODEL_CONCURRENCY, SUBJECTS, SamplingParams
from .openrouter import OpenRouterError, chat


def _existing_keys(path: Path) -> set[tuple[str, str, int]]:
    if not path.exists():
        return set()
    keys = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if "text" in row:
            keys.add((row["model"], row["lang"], row["sample"]))
    return keys


async def collect(run_dir: Path, params: SamplingParams) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_dir / "responses.jsonl"
    params_path = run_dir / "params.json"
    stems = SUBJECTS[params.subject].stems
    record = {**params.__dict__, "stems": {l: stems[l] for l in params.langs}}
    # Subset re-runs (e.g. retrying one model) must not shrink the run's recorded scope.
    if params_path.exists():
        previous = json.loads(params_path.read_text(encoding="utf-8"))
        if previous.get("subject", "dragon") != params.subject:
            raise SystemExit(f"{run_dir.name} is a {previous.get('subject', 'dragon')} run, not {params.subject}")
        record["models"] = list(dict.fromkeys(previous["models"] + params.models))
        record["langs"] = list(dict.fromkeys(previous["langs"] + params.langs))
        record["stems"] = previous["stems"] | record["stems"]
    params_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    done = _existing_keys(out_path)
    semaphores = {m: asyncio.Semaphore(PER_MODEL_CONCURRENCY.get(m, DEFAULT_CONCURRENCY)) for m in params.models}
    lock = asyncio.Lock()
    counts = {"ok": 0, "error": 0}

    async def one(client: httpx.AsyncClient, model: str, lang: str, sample: int) -> None:
        async with semaphores[model]:
            row = {
                "model": model,
                "lang": lang,
                "stem": stems[lang],
                "sample": sample,
                "temperature": params.temperature,
                "max_tokens": params.max_tokens,
            }
            try:
                payload = await chat(
                    client,
                    model,
                    [{"role": "user", "content": stems[lang]}],
                    temperature=params.temperature,
                    max_tokens=params.max_tokens,
                )
                choice = payload["choices"][0]
                row |= {
                    "text": choice["message"].get("content") or "",
                    "finish_reason": choice.get("finish_reason"),
                    "provider": payload.get("provider"),
                    "model_served": payload.get("model"),
                    "cost": (payload.get("usage") or {}).get("cost"),
                }
                counts["ok"] += 1
            except OpenRouterError as exc:
                row["error"] = str(exc)
                counts["error"] += 1
            row["created_at"] = datetime.now(timezone.utc).isoformat()
            async with lock:
                with out_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

    jobs = [
        (m, l, s)
        for m in params.models
        for l in params.langs
        for s in range(params.samples)
        if (m, l, s) not in done
    ]
    print(f"{len(jobs)} calls to make ({len(done)} already done)")
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*(one(client, m, l, s) for m, l, s in jobs))
    print(f"ok {counts['ok']}, errors {counts['error']}")
