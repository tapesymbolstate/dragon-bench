import json
import os
from dataclasses import dataclass, field, replace
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

GENERIC_EN_EXAMPLES = ('Name the concept, not the phrasing: drop wrappers such as "symbol of", "sign of", "brings", '
                       '"associated with", "a kind of".')
GENERIC_TRADITION = ('"eastern" if the response attributes it to East Asian (Chinese, Korean, Japanese) culture, '
                     '"western" if to European/Western culture, otherwise "general".')


@dataclass(frozen=True)
class Subject:
    name: str
    noun: str
    topic: str
    sense: str
    about: str
    stems: dict[str, str]
    self_words: tuple[str, ...]
    en_examples: str = GENERIC_EN_EXAMPLES
    tradition: str = GENERIC_TRADITION


DRAGON = Subject(
    name="dragon",
    noun="a dragon",
    topic="dragons",
    sense="the dragon (the mythical creature or its symbolism)",
    about="mythical_dragon",
    stems={"en": "Dragon is", "ko": "용은", "zh": "龙是", "ja": "竜は"},
    self_words=("dragon", "용", "龍", "龙", "竜", "ドラゴン", "드래곤", "dragons", "りゅう", "たつ"),
    en_examples=('Name the concept, not the phrasing: "sacred" not "sacred symbol", "royalty" not "symbol of royalty", '
                 '"rain" not "brings rain", "fire" not "breathes fire", "legendary" not "legendary animal".'),
    tradition='"eastern" if the response attributes it to East Asian dragons, "western" if to European/Western dragons, '
              'otherwise "general".',
)

# Stems whose connotation is said to split between East Asian and European traditions.
SUBJECTS = {s.name: s for s in [
    DRAGON,
    # 龍 disambiguates 용 (also 용도, a given name) but is itself an East Asian cue; compared against dragon/ko.
    replace(DRAGON, name="dragon_hanja", stems={"ko": "용(龍)은"}),
    Subject("four", "the number 4", "the number 4", "the number 4 (as a number, or its symbolism and associations)",
            "number_4", {"en": "4 is", "ko": "4는", "zh": "4是", "ja": "4は"},
            ("4", "four", "넷", "四", "よん")),
    Subject("thirteen", "the number 13", "the number 13", "the number 13 (as a number, or its symbolism and associations)",
            "number_13", {"en": "13 is", "ko": "13은", "zh": "13是", "ja": "13は"},
            ("13", "thirteen", "십삼", "열셋", "十三", "じゅうさん")),
    Subject("white", "the colour white", "the colour white", "the colour white (or its symbolism and associations)",
            "colour_white", {"en": "White is", "ko": "흰색은", "zh": "白色是", "ja": "白は"},
            ("white", "흰색", "하양", "흰", "白", "白色", "しろ", "ホワイト")),
    Subject("crow", "a crow", "crows", "the crow (the bird or its symbolism)",
            "crow", {"en": "Crow is", "ko": "까마귀는", "zh": "乌鸦是", "ja": "カラスは"},
            ("crow", "crows", "까마귀", "乌鸦", "烏", "鴉", "カラス", "からす")),
    Subject("owl", "an owl", "owls", "the owl (the bird or its symbolism)",
            "owl", {"en": "Owl is", "ko": "부엉이는", "zh": "猫头鹰是", "ja": "フクロウは"},
            ("owl", "owls", "부엉이", "올빼미", "猫头鹰", "梟", "フクロウ", "ふくろう")),
    Subject("bat", "a bat", "bats", "the bat (the flying mammal or its symbolism)",
            "bat_animal", {"en": "Bat is", "ko": "박쥐는", "zh": "蝙蝠是", "ja": "コウモリは"},
            ("bat", "bats", "박쥐", "蝙蝠", "コウモリ", "こうもり")),
    Subject("chrysanthemum", "a chrysanthemum", "chrysanthemums", "the chrysanthemum (the flower or its symbolism)",
            "chrysanthemum", {"en": "Chrysanthemum is", "ko": "국화는", "zh": "菊花是", "ja": "菊は"},
            ("chrysanthemum", "chrysanthemums", "국화", "菊花", "菊", "きく")),
]}

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
    subject: str = "dragon"
    samples: int = 100
    temperature: float = 1.0
    max_tokens: int = 200
    models: list[str] = field(default_factory=lambda: list(MODELS))
    langs: list[str] = field(default_factory=lambda: list(DRAGON.stems))


def run_subject(run_dir: Path) -> Subject:
    params_path = run_dir / "params.json"
    if not params_path.exists():
        raise SystemExit(f"{params_path} not found; run collect first")
    # Runs recorded before subjects existed are all dragon runs.
    return SUBJECTS[json.loads(params_path.read_text(encoding="utf-8")).get("subject", "dragon")]


def api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set")
    return key
