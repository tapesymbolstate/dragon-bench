# Project Status

**Last Updated:** 2026-10-02T23:40+09:00
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-10-02 (evening): README and data published
- ✅ README rewritten around purpose and findings, with a generated header image and the overview heatmap
- ✅ Benchmark outputs under `data/` are now committed to the private repo `tapesymbolstate/dragon-bench` (old `origin` kept as remote `jujumilk3`)
- 🔧 Overview rows are labelled by subject alone unless two runs share a subject

### 2026-10-02: v1 cleaned up and validated, seven more stems screened
- ✅ v1 complete: the last 7 Mistral calls succeeded (3,200 / 3,200 responses and extractions)
- ✅ Taxonomy review of `data/runs/v1/taxonomy.json` (by Claude, not a human; recorded in its `review` key, pre-review copy in `taxonomy.before-review.json`):
  - treasure / treasure guardian (western hoard, labelled positive) → hoarding; omen (mostly 길조/吉兆) → luck; beast (mostly 巨兽) → creature; 四灵 and Draco out of zodiac; fire breath merged into fire; dragon king → water deity; …
  - power, authority, important, hero, festival → neutral: capability and rule describe monsters as well as emperors
- ✅ Extractor validation on 64 stratified responses labelled blind by Claude (`data/runs/v1/validation/`): response type 89%, on-subject 98%, concepts precision 0.82 / recall 0.69, tradition 94%, per-language net valence within ±0.09 of the labels (English lowest on both sides; ko and zh swap places)
- 🔧 Validation found the 15-descriptor cap cut the second half of long answers (27% recall past the 15th concept): English answers lost their eastern part, Chinese answers their western part. Cap is now 30; the 919 capped v1 responses were re-extracted (old file `extractions.cap15.jsonl`)
- ✅ v1 headline after both fixes: net valence lowest in English for 8/8 models (−0.09 … +0.09, mean +0.03), highest in Chinese for 6/8 (mean +0.31, ko +0.26, ja +0.16); eastern-attributed descriptors en 25%, ko 57%, zh 77%, ja 39% (pooled). Before the fixes STATUS said "English lowest for every model", which was 6/8
- ✅ Low-n cells (< 10 on-subject, same-language responses) are masked in heatmaps and flagged in tables; deepseek / 용은 (n=6) is the only one in v1
- ✅ Subjects: `config.SUBJECTS` with per-subject prompt wording; extraction and taxonomy prompts are generic, and for the dragon the extraction prompt reads as before. `dragon_sense` renamed `subject_sense` in v1/smoke data (backup `extractions.before-rename.jsonl`)
- ✅ New runs, each taxonomy reviewed for valence the same way (facts, abilities and uses neutral; stated benefits to people positive):
  - `dragon-hanja` (`용(龍)은`, 8 models × 100, scored with the v1 taxonomy): fixes deepseek (Korean 6% → 100%) but is not neutral — eastern share 55% → 67%, western 11% → 3%, net valence +0.26 → +0.36. Keep `용은` as the main stem
  - `four`, `thirteen`, `white`, `crow`, `owl`, `bat`, `chrysanthemum` (8 models × 4 languages × 20, screening scale)
- Screening results (`data/overview/overview.md`, `overview.png`):
  - 13: "unlucky" 59–64% in every language, western-attributed — the western superstition carries into CJK prompts
  - 4: answers are arithmetic; "unlucky" en 7% vs ko 15%, zh 22%, ja 22%; net valence ≈ 0 everywhere
  - white: purity dominates everywhere (+0.29 … +0.44); mourning zh 40%, ko 22%, en 14%, ja 9%
  - chrysanthemum: en is botany (+0.12), CJK symbolic (+0.29 … +0.33); imperial crest ja 69%; mourning en 26%, ko 24%, ja 16%, zh 6%
  - crow, owl, bat: mostly biology in every language (net ≈ +0.03 … +0.15); owl good fortune ko 16% / ja 25% (부엉이, 不苦労) but zh 0%; bat 福 ≈ 2% even in Chinese
- ✅ New CLI commands `validation-sample`, `validate`, `overview`; heatmap labels pick text colour from cell luminance
- Spend today ≈ $3.90 (key usage 3.09 → 7.00). The OpenRouter account has $10 in credits in total, so about $3.00 is left, and the key is shared with imagen-forge

### 2026-09-30: First full run `v1` (8 models × 4 languages × 100 samples)
- ✅ Pipeline `collect → extract → report` in `src/dragon_bench/` (uv package, CLI `dragon-bench`)
- 🔧 Fixed: a subset `collect --models X` used to overwrite `params.json` and shrink the report to that model; collect now unions the scope and report derives models/langs from the data

## Next Actions (Priority Order)

1. **[HIGH]** Have a human check the taxonomy reviews and validation labels — both were done by Claude. Valence rules to confirm: capability / rule / facts / uses neutral, stated benefits positive (`review` key in each `taxonomy.json`)
2. **[MEDIUM]** Credits: about $3.00 left on a shared $10 account. A full 100-sample run costs about $1.50–2.00 per stem; top up before scaling the screening runs
3. **[MEDIUM]** Scale up the stems that split by language: chrysanthemum, white, four (100 samples). 13, bat and owl mostly show no split at 20 samples
4. **[LOW]** Validate the extractor on a non-dragon run (subjects use the generic prompt, which v1 validation does not cover)
5. **[LOW]** The extractor sometimes drops negation (4 "is not prime" tagged as prime number); neutral, so no effect on valence

## Code Location Map

- `src/dragon_bench/__init__.py` — CLI (`collect`, `extract`, `report`, `validation-sample`, `validate`, `overview`)
- `src/dragon_bench/config.py` — models, `Subject` / `SUBJECTS` (stems, prompt wording, self words), extractor/taxonomy models, per-model concurrency, reasoning fallback
- `src/dragon_bench/openrouter.py` — chat call with retry/backoff; retries with minimal reasoning when an endpoint forbids disabling it
- `src/dragon_bench/collect.py` — resumable sampling to `responses.jsonl`; refuses to mix subjects in one run
- `src/dragon_bench/extract.py` — script-based language check, schema-constrained extraction (cap 30), span validation, taxonomy build (never overwrites existing valence labels)
- `src/dragon_bench/report.py` — aggregation, low-n masking, heatmaps (matplotlib, CJK fonts from macOS), CSV and Markdown tables
- `src/dragon_bench/validate.py` — stratified blind sample, label-vs-extractor comparison
- `src/dragon_bench/overview.py` — cross-run net valence / tradition / top concepts
- `data/runs/<run>/` — outputs (tracked; `smoke*` pipeline tests and `extractions.before-rename.jsonl` are gitignored); `data/overview/` — cross-run summary shown in the README
- `docs/images/hero.jpg` — README header image (generated with Codex)

## How to Run

```bash
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY=' ~/Projects/imagen-forge/.env | cut -d= -f2- | tr -d '"')"
uv run dragon-bench collect v1 --samples 100                 # dragon is the default subject
uv run dragon-bench collect crow --subject crow --samples 20
uv run dragon-bench extract <run>
uv run dragon-bench report <run>                              # no API calls; re-run after editing taxonomy.json
uv run dragon-bench validation-sample <run> && uv run dragon-bench validate <run>
uv run dragon-bench overview v1 dragon-hanja four thirteen white crow owl bat chrysanthemum
```

## Known Issues

- New OpenRouter accounts are limited to 20 requests/minute on OpenAI and Anthropic models; concurrency for those is 2 (`PER_MODEL_CONCURRENCY`). Six of the seven 20-sample runs had 2 transient failures each, which the second `collect` pass resolved
- `mistralai/mistral-small-2603` is intermittently rate-limited upstream
- `google/gemini-3.5-flash-lite` cannot run without reasoning; it runs with `effort: low` (hidden), so it is not strictly first-impulse like the others
- Extractor (`gemini-2.5-flash-lite`) and taxonomy (`gemini-3.8-flash`) models are Google models; their judgements are not independent of the Google model under test. The v1 validation labels come from Claude, a different family, but Claude's own model (haiku-4.5) is also under test
- 20-sample runs give ±10-point concept shares per cell; compare languages on the means over models, not single cells
