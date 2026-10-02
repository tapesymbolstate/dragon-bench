# dragon-bench

Measures which associations language models reach for when given nothing but a bare subject stem such as `Dragon is` / `용은` / `龙是` / `竜は`, and how those associations shift with the prompt language. Dragons are the first probe because their connotation famously flips between East Asian (auspicious, royal, water and rain) and European (monstrous, fiery, hoarding) traditions. Other subjects said to split the same way are defined in `src/dragon_bench/config.py` (`SUBJECTS`): the numbers 4 and 13, white, crow, owl, bat, chrysanthemum, and `용(龍)은` as a disambiguated Korean dragon stem.

No instruction, persona or cultural frame is added. Each model gets the stem alone as the user message, sampled at temperature 1.0 (100 times per model and language for the dragon), so whatever comes back — a definition, a clarification question, a list of senses, a story — is the model's unprompted default. The pipeline then filters and normalises the answers instead of constraining the prompt.

## Pipeline

1. **collect** — `stem` as the only user message → OpenRouter chat completion. Reasoning is disabled where the endpoint allows it (retried with minimal reasoning where it is mandatory). Every call is one JSONL row with model, served model, provider, cost and a UTC ISO 8601 timestamp; re-running resumes and retries failures. A run holds one subject.
2. **extract** — filtering and normalisation:
   - script-based language detection; answers in a different language than the stem are counted, then excluded from descriptor stats;
   - an extractor model (`google/gemini-2.5-flash-lite`, temperature 0, JSON schema) labels the response type (definition, completion, clarification, multi_sense, refusal, other), whether it treats the stem as the subject at all (`subject_sense`), and lists up to 30 descriptors with an exact text span, native lemma, English concept tag and the tradition it is attributed to (eastern / western / general);
   - descriptors are kept only if the span actually occurs in the answer, belongs to the subject's sense and is not the subject word itself;
   - a taxonomy step (`google/gemini-3.8-flash`) merges near-synonymous concept tags into canonical concepts — seeded from the 300 most frequent tags in one call, then extended in batches — and labels each canonical concept positive / neutral / negative. Later batches never overwrite a label already in `taxonomy.json`, so hand corrections survive re-extraction.
3. **report** — per model × language: filtering funnel, net valence, tradition split, top concepts; heatmaps of concept frequency (share of on-subject responses that mention the concept at least once) per language and across languages. Cells with fewer than 10 on-subject, same-language responses are marked *low n* and left out of the heatmaps.
4. **validation** — `validation-sample` draws a stratified sample (2 responses per model × language by default) with only the text; labels written to `validation/labels.jsonl` are compared by `validate` with what the report counts (concepts of on-subject, same-language responses after the taxonomy), giving precision / recall, tradition agreement and per-language net valence for both sides.
5. **overview** — net valence, tradition shares and top concepts per subject × language across runs, each model weighted once.

## Run

```bash
export OPENROUTER_API_KEY=...        # never commit it; data/ is gitignored
uv run dragon-bench collect v1 --samples 100            # --subject dragon is the default
uv run dragon-bench extract v1
uv run dragon-bench report v1
uv run dragon-bench collect crow --subject crow --samples 20
uv run dragon-bench validation-sample v1                # then write validation/labels.jsonl
uv run dragon-bench validate v1
uv run dragon-bench overview v1 dragon-hanja crow
```

`collect` accepts `--models` and `--langs` to run a subset. Outputs land in `data/runs/<run>/`: `responses.jsonl`, `extractions.jsonl`, `taxonomy.json`, `report/` (`report.md`, `summary.csv`, `descriptors.csv`, `valence.png`, `words_<lang>.png`, `words_cross.png`) and `validation/`; the overview goes to `data/overview/`.

## Caveats

- The extractor and taxonomy models have their own cultural leanings; spans are verified against the text, but concept tags and valence labels are model judgements. `taxonomy.json` is meant to be reviewed by hand; the review of `v1` is recorded in its `review` key. Capability and rule (power, authority, control) count as neutral, since the same words describe monsters and emperors.
- The descriptor cap was 15 at first. Answers that describe one tradition after the other lost the second one (27% recall past the 15th concept in validation), which inflated whichever tradition came first; the cap is now 30.
- `용은` is ambiguous (the noun 용도, a given name); the extractor's `subject_sense` flag and the per-descriptor `about` field are what filter those readings out. `용(龍)은` removes the ambiguity but adds an East Asian cue.
- Concept shares are per response (presence), so a long answer counts the same as a short one.
