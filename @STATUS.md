# Project Status

**Last Updated:** 2026-09-30T22:40+09:00
**Last Author:** Claude Code

## Recent Changes (Latest First)

### 2026-09-30: First full run `v1` (8 models × 4 languages × 100 samples)
- ✅ Pipeline `collect → extract → report` in `src/dragon_bench/` (uv package, CLI `dragon-bench`)
- ✅ 3,193 / 3,200 responses collected (7 Mistral calls still failing upstream with 429); 3,193 extractions, 0 extractor errors
- ✅ Taxonomy: 1,872 raw concept tags → 235 canonical concepts with valence (`data/runs/v1/taxonomy.json`)
- ✅ Report: `data/runs/v1/report/` — `valence.png`, `words_{en,ko,zh,ja}.png`, `words_cross.png`, `report.md`, `summary.csv`, `descriptors.csv`
- ✅ Spend for the day on the OpenRouter key: about $2.06 (collection $0.90, the rest extraction + taxonomy + smoke tests)
- Headline: net valence is lowest in English for every model (−0.02 … +0.24) and highest in Chinese for most (up to +0.64); eastern-attributed descriptors are 19% in en, 56% ko, 78% zh, 40% ja
- 🔧 Fixed: a subset `collect --models X` used to overwrite `params.json` and shrink the report to that model; collect now unions the scope and report derives models/langs from the data

## Next Actions (Priority Order)

1. **[HIGH]** Hand-review `data/runs/v1/taxonomy.json` — a few merges are doubtful (e.g. "omen" → luck, "boss" → authority); edit the mapping and re-run `report` (no API calls needed)
2. **[MEDIUM]** Validate the extractor: hand-label ~50 responses and compare concept tags / valence against `extractions.jsonl`
3. **[MEDIUM]** Retry the last 7 Mistral calls: `uv run dragon-bench collect v1 --models mistralai/mistral-small-2603` then `extract` + `report`
4. **[LOW]** More stems with split connotations (`4`, `13`, white, crow, owl, bat, chrysanthemum) as new runs; consider `용(龍)은` to cut the 용도/name ambiguity
5. **[LOW]** Deepseek answers `용은` in Chinese 94% of the time — cell is effectively empty; decide whether to report it separately

## Code Location Map

- `src/dragon_bench/__init__.py` — CLI (`collect`, `extract`, `report`)
- `src/dragon_bench/config.py` — models, stems, extractor/taxonomy models, per-model concurrency, reasoning fallback
- `src/dragon_bench/openrouter.py` — chat call with retry/backoff; retries with minimal reasoning when an endpoint forbids disabling it
- `src/dragon_bench/collect.py` — resumable sampling to `responses.jsonl`
- `src/dragon_bench/extract.py` — script-based language check, schema-constrained extraction, span validation, taxonomy build
- `src/dragon_bench/report.py` — aggregation, heatmaps (matplotlib, CJK fonts from macOS), CSV and Markdown tables
- `data/runs/<run>/` — outputs (gitignored)

## How to Run

```bash
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY=' ~/Projects/imagen-forge/.env | cut -d= -f2- | tr -d '"')"
uv run dragon-bench collect v1 --samples 100
uv run dragon-bench extract v1
uv run dragon-bench report v1
```

## Known Issues

- New OpenRouter accounts are limited to 20 requests/minute on OpenAI and Anthropic models; concurrency for those is 2 (`PER_MODEL_CONCURRENCY`)
- `mistralai/mistral-small-2603` is intermittently rate-limited upstream
- `google/gemini-3.5-flash-lite` cannot run without reasoning; it runs with `effort: low` (hidden), so it is not strictly first-impulse like the others
- Extractor (`gemini-2.5-flash-lite`) and taxonomy (`gemini-3.8-flash`) models are Google models; their judgements are not independent of the Google model under test
- Not committed yet (git repo initialised by `uv init`, no commits)
