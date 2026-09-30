# dragon-bench

Measures which associations language models reach for when given nothing but a bare subject stem such as `Dragon is` / `용은` / `龙是` / `竜は`, and how those associations shift with the prompt language. Dragons are the first probe because their connotation famously flips between East Asian (auspicious, royal, water and rain) and European (monstrous, fiery, hoarding) traditions.

No instruction, persona or cultural frame is added. Each model gets the stem alone as the user message, sampled 100 times at temperature 1.0, so whatever comes back — a definition, a clarification question, a list of senses, a story — is the model's unprompted default. The pipeline then filters and normalises the answers instead of constraining the prompt.

## Pipeline

1. **collect** — `stem` as the only user message → OpenRouter chat completion. Reasoning is disabled where the endpoint allows it (retried with minimal reasoning where it is mandatory). Every call is one JSONL row with model, served model, provider, cost and a UTC ISO 8601 timestamp; re-running resumes and retries failures.
2. **extract** — filtering and normalisation:
   - script-based language detection; answers in a different language than the stem are counted, then excluded from descriptor stats;
   - an extractor model (`google/gemini-2.5-flash-lite`, temperature 0, JSON schema) labels the response type (definition, completion, clarification, multi_sense, refusal, other), whether it treats the stem as the mythical dragon at all, and lists descriptors with an exact text span, native lemma, English concept tag and the tradition it is attributed to (eastern / western / general);
   - descriptors are kept only if the span actually occurs in the answer, belongs to the dragon sense and is not the word "dragon" itself;
   - a taxonomy step (`google/gemini-3.8-flash`) merges near-synonymous concept tags into canonical concepts — seeded from the 300 most frequent tags in one call, then extended in batches — and labels each canonical concept positive / neutral / negative.
3. **report** — per model × language: filtering funnel, net valence, tradition split, top concepts; heatmaps of concept frequency (share of dragon-sense responses that mention the concept at least once) per language and across languages.

## Run

```bash
export OPENROUTER_API_KEY=...        # never commit it; data/ is gitignored
uv run dragon-bench collect v1 --samples 100
uv run dragon-bench extract v1
uv run dragon-bench report v1
```

`collect` accepts `--models` and `--langs` to run a subset. Outputs land in `data/runs/<run>/`: `responses.jsonl`, `extractions.jsonl`, `taxonomy.json`, and `report/` (`report.md`, `summary.csv`, `descriptors.csv`, `valence.png`, `words_<lang>.png`, `words_cross.png`).

## Caveats

- The extractor and taxonomy models have their own cultural leanings; spans are verified against the text, but concept tags and valence labels are model judgements. `taxonomy.json` is meant to be reviewed by hand.
- `용은` is ambiguous (the noun 용도, a given name); the extractor's `dragon_sense` flag and the per-descriptor `about` field are what filter those readings out.
- Concept shares are per response (presence), so a long answer counts the same as a short one.
