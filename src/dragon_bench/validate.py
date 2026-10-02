import json
import random
from collections import Counter
from pathlib import Path

from .extract import RESPONSE_TYPES, _read_jsonl


def _key(r: dict) -> tuple[str, str, int]:
    return r["model"], r["lang"], r["sample"]


def draw_sample(run_dir: Path, per_cell: int, seed: int = 0) -> None:
    out_dir = run_dir / "validation"
    out_dir.mkdir(exist_ok=True)
    responses = sorted((r for r in _read_jsonl(run_dir / "responses.jsonl") if "text" in r), key=_key)
    by_cell: dict[tuple[str, str], list[dict]] = {}
    for r in responses:
        by_cell.setdefault((r["model"], r["lang"]), []).append(r)
    rng = random.Random(seed)
    picked = [r for cell in sorted(by_cell) for r in rng.sample(by_cell[cell], min(per_cell, len(by_cell[cell])))]
    # The sample carries only what a labeller should see, so labels stay blind to the extractor's output.
    with (out_dir / "sample.jsonl").open("w", encoding="utf-8") as f:
        for r in picked:
            f.write(json.dumps({k: r[k] for k in ("model", "lang", "sample", "stem", "text")}, ensure_ascii=False) + "\n")
    taxonomy = json.loads((run_dir / "taxonomy.json").read_text(encoding="utf-8"))
    (out_dir / "codebook.txt").write_text(
        "\n".join(f"{c}: {v}" for c, v in sorted(taxonomy["valence"].items())) + "\n", encoding="utf-8")
    print(f"{len(picked)} responses written to {out_dir / 'sample.jsonl'}; label them in labels.jsonl as "
          '{"model", "lang", "sample", "response_type", "subject_sense", "concepts": [{"concept", "tradition"}]}')


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def _net(concepts: set[str], valence: dict[str, str]) -> float | None:
    labels = [valence.get(c) for c in concepts]
    labeled = [v for v in labels if v]
    return (labeled.count("positive") - labeled.count("negative")) / len(labeled) if labeled else None


def validate(run_dir: Path) -> None:
    out_dir = run_dir / "validation"
    labels = {_key(r): r for r in _read_jsonl(out_dir / "labels.jsonl")}
    extractions = {_key(r): r for r in _read_jsonl(run_dir / "extractions.jsonl") if "descriptors" in r}
    taxonomy = json.loads((run_dir / "taxonomy.json").read_text(encoding="utf-8"))
    mapping, valence = taxonomy["mapping"], taxonomy["valence"]

    type_pairs, sense_pairs = Counter(), Counter()
    tp = fp = fn = 0
    tradition_match = tradition_total = 0
    missed, extra = Counter(), Counter()
    per_lang: dict[str, dict[str, list[float]]] = {}
    item_diffs = []
    for key, label in labels.items():
        e = extractions[key]
        type_pairs[(label["response_type"], e["response_type"])] += 1
        sense_pairs[(label["subject_sense"], e["subject_sense"])] += 1
        # Compare what the report actually counts: concepts of on-subject, same-language responses.
        if not e["lang_match"]:
            continue
        mine = {mapping.get(c["concept"], c["concept"]): c["tradition"] for c in label["concepts"]} \
            if label["subject_sense"] else {}
        theirs: dict[str, set[str]] = {}
        if e["subject_sense"]:
            for d in e["descriptors"]:
                theirs.setdefault(mapping.get(d["en"], d["en"]), set()).add(d["tradition"])
        tp += len(mine.keys() & theirs.keys())
        fn += len(mine.keys() - theirs.keys())
        fp += len(theirs.keys() - mine.keys())
        missed.update(mine.keys() - theirs.keys())
        extra.update(theirs.keys() - mine.keys())
        for c in mine.keys() & theirs.keys():
            tradition_total += 1
            tradition_match += mine[c] in theirs[c]
        nm, nt = _net(set(mine), valence), _net(set(theirs), valence)
        cell = per_lang.setdefault(key[1], {"mine": [], "theirs": []})
        if nm is not None:
            cell["mine"].append(nm)
        if nt is not None:
            cell["theirs"].append(nt)
        if nm is not None and nt is not None:
            item_diffs.append(nt - nm)

    n = len(labels)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    type_agree = sum(v for (a, b), v in type_pairs.items() if a == b)
    sense_agree = sum(v for (a, b), v in sense_pairs.items() if a == b)
    lines = [
        f"# Extractor validation: {run_dir.name}", "",
        f"{n} hand-labelled responses (stratified, `validation/sample.jsonl`), compared with `extractions.jsonl` "
        "after the run's taxonomy is applied to both sides.", "",
        f"- response_type agreement: {type_agree}/{n} ({type_agree / n:.0%})",
        f"- subject_sense agreement: {sense_agree}/{n} ({sense_agree / n:.0%})",
        f"- concepts (on-subject, same-language responses): precision {precision:.2f}, recall {recall:.2f}, "
        f"F1 {f1:.2f} (tp {tp}, fp {fp}, fn {fn})",
        f"- tradition agreement on shared concepts: {tradition_match}/{tradition_total}"
        + (f" ({tradition_match / tradition_total:.0%})" if tradition_total else ""),
        f"- per-response net valence, extractor minus labels: mean {_mean(item_diffs):+.2f}, "
        f"mean absolute {_mean([abs(d) for d in item_diffs]):.2f} (n={len(item_diffs)})", "",
        "## Net valence by language (mean over responses, concept presence)", "",
        "| lang | labels | extractor | n |", "|---|---|---|---|",
    ]
    for lang in sorted(per_lang):
        cell = per_lang[lang]
        lines.append(f"| {lang} | {_mean(cell['mine']):+.2f} | {_mean(cell['theirs']):+.2f} | {len(cell['mine'])} |")
    lines += ["", "## response_type confusion (label → extractor)", "",
              "| label \\ extractor | " + " | ".join(RESPONSE_TYPES) + " |",
              "|---|" + "---|" * len(RESPONSE_TYPES)]
    for a in RESPONSE_TYPES:
        if any(type_pairs[(a, b)] for b in RESPONSE_TYPES):
            lines.append(f"| {a} | " + " | ".join(str(type_pairs[(a, b)] or "") for b in RESPONSE_TYPES) + " |")
    lines += ["", "## subject_sense (label, extractor): " +
              ", ".join(f"{a}/{b} {v}" for (a, b), v in sorted(sense_pairs.items())), "",
              "## Concepts the extractor missed most", "",
              ", ".join(f"{c} ({v})" for c, v in missed.most_common(25)), "",
              "## Concepts only the extractor found", "",
              ", ".join(f"{c} ({v})" for c, v in extra.most_common(25)), ""]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:9]))
