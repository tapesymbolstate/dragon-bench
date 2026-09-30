import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "data" / "runs"

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

MODELS = [
    "openai/gpt-6-luna",
    "anthropic/claude-haiku-4.5",
    "google/gemini-3.5-flash-lite",
    "meta-llama/llama-4-maverick",
    "mistralai/mistral-small-2603",
    "deepseek/deepseek-v4.1-flash",
    "qwen/qwen3.8-flash",
    "upstage/solar-mini4",
]

STEMS = {
    "en": "Dragon is",
    "ko": "용은",
    "zh": "龙是",
    "ja": "竜は",
}

EXTRACTOR_MODEL = "google/gemini-2.5-flash-lite"
# One stronger call over the whole concept list; not one of the benchmarked models.
TAXONOMY_MODEL = "google/gemini-3.8-flash"

# Reasoning is disabled by default so every model answers from its first impulse;
# endpoints that refuse to run without it are retried with the smallest budget instead.
FALLBACK_REASONING = {"effort": "low", "exclude": True}
REASONING_TOKEN_HEADROOM = 1000

# New OpenRouter accounts get 20 requests/minute on these; mistral is rate-limited upstream.
PER_MODEL_CONCURRENCY = {"openai/gpt-6-luna": 2, "anthropic/claude-haiku-4.5": 2, "mistralai/mistral-small-2603": 3}
DEFAULT_CONCURRENCY = 6


@dataclass(frozen=True)
class SamplingParams:
    samples: int = 100
    temperature: float = 1.0
    max_tokens: int = 200
    models: list[str] = field(default_factory=lambda: list(MODELS))
    langs: list[str] = field(default_factory=lambda: list(STEMS))


def api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set")
    return key
