import asyncio
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import httpx

from .config import EXTRACTOR_MODEL, TAXONOMY_MODEL, Subject, run_subject
from .openrouter import OpenRouterError, chat

LANG_NAMES = {"en": "English", "ko": "Korean", "zh": "Chinese", "ja": "Japanese"}
RESPONSE_TYPES = ["definition", "completion", "clarification", "multi_sense", "refusal", "other"]
TRADITIONS = ["eastern", "western", "general"]
VALENCES = ["positive", "neutral", "negative"]
# 15 truncated long answers that describe one tradition after the other (validation on v1: 27% recall
# past the 15th concept), which inflated whichever tradition the answer described first.
MAX_DESCRIPTORS = 30


def extraction_schema(subject: Subject) -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "subject_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["response_type", "subject_sense", "descriptors"],
                "properties": {
                    "response_type": {"type": "string", "enum": RESPONSE_TYPES},
                    "subject_sense": {"type": "boolean"},
                    "descriptors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["text", "lemma", "en", "tradition", "about"],
                            "properties": {
                                "text": {"type": "string"},
                                "about": {"type": "string", "enum": [subject.about, "other"]},
                                "lemma": {"type": "string"},
                                "en": {"type": "string"},
                                "tradition": {"type": "string", "enum": TRADITIONS},
                            },
                        },
                    },
                },
            },
        },
    }


EXTRACTION_PROMPT = """You extract data from one chatbot response. The chatbot was sent only the text fragment {stem!r} ({language}) with no other context.

Return JSON with:
- response_type, the dominant one of:
  "definition": explains or describes what {noun} is;
  "completion": continues the fragment as a sentence, poem or story;
  "clarification": mainly asks the user what they meant;
  "multi_sense": lists several possible meanings of the fragment;
  "refusal"; "other".
- subject_sense: true if any part of the response talks about {sense}; false if it only treats the fragment as something else (a person's name, another word, a grammar question).
- descriptors: words or short phrases (at most 4 words) from the response that say what {noun} is, is like, symbolises, represents or does: attributes, roles, symbolism, associations. Take them only from the parts about {topic}. Skip words about the conversation itself (sentence, context, meaning, question, example), headings and generic filler.
  "text": copied exactly as it appears in the response.
  "lemma": its dictionary form in the response's own language.
  "en": the core concept as one lowercase English word, two only if one cannot carry it. {en_examples}
  "tradition": {tradition}
  "about": "{about}" if it describes {sense}; "other" if it belongs to another sense of the fragment (a brand, a person, a word, a game character).
  Never include the word for {name} itself ({self_words}) as a descriptor.
  At most {max_descriptors}, in order of appearance, no duplicate lemmas.

Response:
<<<
{text}
>>>"""

TAXONOMY_SEED_PROMPT = """Below are concept tags that chatbots used when describing {topic}, each with the number of responses that used it.

Build a canonical vocabulary:
- Map every tag to a canonical tag. Merge tags that name the same idea: spelling variants, singular/plural, adjective/noun forms and near-synonyms (for example "mythical creature", "legendary creature", "imaginary creature"; "luck", "good fortune", "auspicious"). Keep genuinely different ideas apart (for example "fire" and "power", "wisdom" and "magic").
- A canonical tag is lowercase, 1-2 words, preferably the most used member of its group.
- Give every canonical tag the connotation it lends {noun}:
  "positive": auspicious, benevolent, noble, lucky, wise, protective, sacred, prosperous, pure and the like;
  "negative": evil, destructive, threatening, greedy, dangerous, monstrous, unlucky, ominous, tied to death or misfortune and the like;
  "neutral": physical description, category, habitat, culture, capability or other neutral facts.

Return JSON: {{"mapping": {{"<tag>": "<canonical>"}}, "valence": {{"<canonical>": "positive|neutral|negative"}}}}. Include every tag exactly as given.

Tags:
{items}"""

TAXONOMY_EXTEND_PROMPT = """Existing canonical vocabulary for concepts used to describe {topic} (tag: connotation):
{vocab}

Map each new tag below to an existing canonical tag when it names the same idea (synonym, variant, inflection). Otherwise map it to a new canonical tag (lowercase, 1-2 words) and give that new tag a connotation ("positive", "neutral" or "negative", same meaning as the existing labels).

Return JSON: {{"mapping": {{"<new tag>": "<canonical>"}}, "valence": {{"<new canonical>": "positive|neutral|negative"}}}}. Include every new tag exactly as given.

New tags:
{items}"""


def detect_script_lang(text: str) -> str:
    counts = {"hangul": 0, "kana": 0, "han": 0, "latin": 0}
    for ch in text:
        if "가" <= ch <= "힣" or "ᄀ" <= ch <= "ᇿ" or "㄰" <= ch <= "㆏":
            counts["hangul"] += 1
        elif "぀" <= ch <= "ヿ":
            counts["kana"] += 1
        elif "一" <= ch <= "鿿":
            counts["han"] += 1
        elif ch.isascii() and ch.isalpha():
            counts["latin"] += 1
    total = sum(counts.values())
    if total == 0:
        return "none"
    if counts["hangul"] / total > 0.3:
        return "ko"
    # Japanese mixes kanji heavily, so a modest kana share is already decisive.
    if counts["kana"] / total > 0.1:
        return "ja"
    if counts["han"] / total > 0.3:
        return "zh"
    if counts["latin"] / total > 0.5:
        return "en"
    return "other"


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).casefold()
    return re.sub(r"[\s*_`\"'“”‘’「」『』]+", " ", s).strip()


def validate_descriptors(text: str, descriptors: list[dict], subject: Subject) -> tuple[list[dict], int]:
    haystack = _norm(text)
    self_words = {_norm(w) for w in subject.self_words}
    kept, seen = [], set()
    for d in descriptors:
        lemma_key = (_norm(d["lemma"]), d["tradition"])
        if (
            d["about"] == "other"
            or not d["text"].strip()
            or _norm(d["text"]) not in haystack
            or _norm(d["lemma"]) in self_words
            or _norm(d["en"]) in self_words
            or lemma_key in seen
        ):
            continue
        seen.add(lemma_key)
        kept.append({**d, "en": _norm(d["en"])})
    return kept, len(descriptors) - len(kept)


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


async def extract(run_dir: Path) -> None:
    subject = run_subject(run_dir)
    schema = extraction_schema(subject)
    responses = [r for r in _read_jsonl(run_dir / "responses.jsonl") if "text" in r]
    out_path = run_dir / "extractions.jsonl"
    done = {(r["model"], r["lang"], r["sample"]) for r in _read_jsonl(out_path) if "descriptors" in r}
    todo = [r for r in responses if (r["model"], r["lang"], r["sample"]) not in done]
    print(f"{len(todo)} responses to extract ({len(done)} already done)")
    sem = asyncio.Semaphore(16)
    lock = asyncio.Lock()

    async def one(client: httpx.AsyncClient, r: dict) -> None:
        detected = detect_script_lang(r["text"])
        row = {"model": r["model"], "lang": r["lang"], "sample": r["sample"], "detected_lang": detected,
               "lang_match": detected == r["lang"]}
        if not r["text"].strip():
            row |= {"response_type": "other", "subject_sense": False, "descriptors": [], "dropped": 0}
        else:
            prompt = EXTRACTION_PROMPT.format(
                stem=r["stem"], language=LANG_NAMES[r["lang"]], text=r["text"], noun=subject.noun, topic=subject.topic,
                sense=subject.sense, about=subject.about, name=subject.self_words[0],
                self_words=", ".join(subject.self_words), en_examples=subject.en_examples, tradition=subject.tradition,
                max_descriptors=MAX_DESCRIPTORS)
            parsed = None
            async with sem:
                # The extractor occasionally emits truncated JSON; a slightly warmer retry usually recovers.
                for attempt in range(3):
                    try:
                        payload = await chat(client, EXTRACTOR_MODEL, [{"role": "user", "content": prompt}],
                                             temperature=0.2 * attempt, max_tokens=4000,
                                             response_format=schema)
                        parsed = json.loads(payload["choices"][0]["message"]["content"])
                        row.pop("error", None)
                        break
                    except (OpenRouterError, json.JSONDecodeError, KeyError) as exc:
                        row["error"] = str(exc)[:300]
            if parsed is not None:
                kept, dropped = validate_descriptors(r["text"], parsed["descriptors"], subject)
                row |= {"response_type": parsed["response_type"], "subject_sense": parsed["subject_sense"],
                        "descriptors": kept, "dropped": dropped}
        async with lock:
            with out_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    async with httpx.AsyncClient() as client:
        await asyncio.gather(*(one(client, r) for r in todo))
        await build_taxonomy(client, run_dir, subject)


async def build_taxonomy(client: httpx.AsyncClient, run_dir: Path, subject: Subject, seed_size: int = 300,
                         batch_size: int = 150) -> None:
    path = run_dir / "taxonomy.json"
    taxonomy = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"mapping": {}, "valence": {}}
    counts = Counter(d["en"] for r in _read_jsonl(run_dir / "extractions.jsonl") for d in r.get("descriptors", []))
    missing = [c for c, _ in counts.most_common() if c not in taxonomy["mapping"]]
    print(f"{len(missing)} concepts to canonicalise ({len(counts)} total)")

    async def ask(prompt: str, batch: list[str]) -> None:
        payload = await chat(client, TAXONOMY_MODEL, [{"role": "user", "content": prompt}],
                             temperature=0, max_tokens=16000, response_format={"type": "json_object"})
        result = json.loads(payload["choices"][0]["message"]["content"])
        # Labels already in the file may have been corrected by hand; only new canonicals take the model's label.
        taxonomy["valence"] |= {k: v for k, v in result.get("valence", {}).items()
                                if v in VALENCES and k not in taxonomy["valence"]}
        taxonomy["mapping"] |= {k: v for k, v in result.get("mapping", {}).items() if k in batch}
        path.write_text(json.dumps(taxonomy, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    # Seeding from the most frequent tags in one call keeps synonym groups consistent;
    # later batches can only attach to that vocabulary or add to it.
    if not taxonomy["mapping"] and missing:
        seed = missing[:seed_size]
        await ask(TAXONOMY_SEED_PROMPT.format(topic=subject.topic, noun=subject.noun,
                                              items="\n".join(f"{c} ({counts[c]})" for c in seed)), seed)
        missing = [c for c in missing if c not in taxonomy["mapping"]]
    for i in range(0, len(missing), batch_size):
        batch = missing[i : i + batch_size]
        vocab = "\n".join(f"{c}: {v}" for c, v in sorted(taxonomy["valence"].items()))
        await ask(TAXONOMY_EXTEND_PROMPT.format(topic=subject.topic, vocab=vocab, items="\n".join(batch)), batch)
    unmapped = [c for c in counts if c not in taxonomy["mapping"]]
    unlabeled = {v for v in taxonomy["mapping"].values() if v not in taxonomy["valence"]}
    print(f"canonical concepts: {len(set(taxonomy['mapping'].values()))}, unmapped {len(unmapped)}, "
          f"canonicals without valence {len(unlabeled)}")
