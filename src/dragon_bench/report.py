import csv
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .config import MODELS, run_subject
from .extract import RESPONSE_TYPES, _read_jsonl

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
SEQUENTIAL = LinearSegmentedColormap.from_list(
    "blue_seq", [SURFACE, "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
)
DIVERGING = LinearSegmentedColormap.from_list("red_gray_blue", ["#b3302f", "#e34948", "#f0efec", "#2a78d6", "#184f95"])
LANG_ORDER = ["en", "ko", "zh", "ja"]
TOP_WORDS_PER_LANG = 25
TOP_GLOSSES = 30
# Below this many on-subject, same-language responses a cell's shares and valence are noise
# (deepseek answers 용은 in Chinese 94% of the time), so it is shown as missing.
MIN_CELL_N = 10

plt.rcParams.update({
    "font.family": ["Arial Unicode MS", "Apple SD Gothic Neo", "Hiragino Sans", "PingFang SC"],
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "text.color": INK,
    "axes.labelcolor": INK_SECONDARY,
    "xtick.color": INK_SECONDARY,
    "ytick.color": INK_SECONDARY,
    "axes.edgecolor": SURFACE,
})


def _key(r: dict) -> tuple[str, str, int]:
    return r["model"], r["lang"], r["sample"]


def _lemma(s: str) -> str:
    return unicodedata.normalize("NFKC", s).strip().casefold()


def _short(model: str) -> str:
    return model.split("/", 1)[1]


def load(run_dir: Path) -> tuple[list[dict], dict[str, str]]:
    responses = {_key(r): r for r in _read_jsonl(run_dir / "responses.jsonl") if "text" in r}
    rows = [{**responses[_key(e)], **e} for e in _read_jsonl(run_dir / "extractions.jsonl")
            if "descriptors" in e and _key(e) in responses]
    taxonomy_path = run_dir / "taxonomy.json"
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8")) if taxonomy_path.exists() else {"mapping": {}, "valence": {}}
    for r in rows:
        for d in r["descriptors"]:
            d["raw_en"] = d["en"]
            d["en"] = taxonomy["mapping"].get(d["en"], d["en"])
    return rows, taxonomy["valence"]


def aggregate(rows: list[dict], valence: dict[str, str]) -> dict:
    cells: dict[tuple[str, str], dict] = defaultdict(lambda: {
        "n": 0, "lang_match": 0, "sense": 0, "types": Counter(), "glosses": Counter(),
        "valence": Counter(), "tradition": Counter(),
    })
    # Concepts (English glosses) are the counting unit in every language; the most common
    # native lemma per concept is kept only for labelling.
    gloss_of: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for r in rows:
        c = cells[(r["model"], r["lang"])]
        c["n"] += 1
        c["lang_match"] += r["lang_match"]
        c["types"][r["response_type"]] += 1
        if not r["subject_sense"] or not r["lang_match"]:
            continue
        c["sense"] += 1
        # Presence per response, so one verbose answer cannot outweigh a hundred terse ones.
        c["glosses"].update({d["en"] for d in r["descriptors"]})
        for d in r["descriptors"]:
            gloss_of[(r["lang"], d["en"])][_lemma(d["lemma"])] += 1
            c["valence"][valence.get(d["en"], "unlabeled")] += 1
            c["tradition"][d["tradition"]] += 1
    return {"cells": cells, "gloss_of": gloss_of}


def _usable(c: dict | None) -> bool:
    return bool(c) and c["sense"] >= MIN_CELL_N


def _net_valence(c: dict) -> float | None:
    labeled = c["valence"]["positive"] + c["valence"]["neutral"] + c["valence"]["negative"]
    return (c["valence"]["positive"] - c["valence"]["negative"]) / labeled if labeled else None


def _heatmap(ax, matrix, rows, cols, cmap, vmin, vmax, annotate=False, fmt="{:+.2f}"):
    im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(cols)), cols, rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(len(rows)), rows, fontsize=8)
    ax.set_xticks([x - 0.5 for x in range(1, len(cols))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(rows))], minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)
    ax.tick_params(which="both", length=0)
    if annotate:
        for i, row in enumerate(matrix):
            for j, v in enumerate(row):
                if v == v:
                    r, g, b, _ = cmap((v - vmin) / (vmax - vmin))
                    dark = 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.5
                    ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=8,
                            color="#ffffff" if dark else INK)
    return im


def plot_valence(agg: dict, models: list[str], langs: list[str], out: Path) -> None:
    cells = [[agg["cells"].get((m, l)) for l in langs] for m in models]
    matrix = [[_net_valence(c) if _usable(c) else float("nan") for c in row] for row in cells]
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    im = _heatmap(ax, matrix, [_short(m) for m in models], langs, DIVERGING, -1, 1, annotate=True)
    for i, row in enumerate(cells):
        for j, c in enumerate(row):
            if c and not _usable(c):
                ax.text(j, i, f"n={c['sense']}", ha="center", va="center", fontsize=7, color=MUTED)
    ax.xaxis.tick_top()
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    ax.set_title(f"Net valence of {agg['subject']} descriptors (positive − negative) / all", fontsize=9, color=INK,
                 pad=24)
    cb = fig.colorbar(im, ax=ax, fraction=0.05)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=7, colors=MUTED, length=0)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_words_by_lang(agg: dict, models: list[str], lang: str, out: Path) -> list[tuple[str, str]]:
    total = Counter()
    for m in models:
        c = agg["cells"].get((m, lang))
        if _usable(c):
            total.update({k: v / c["sense"] for k, v in c["glosses"].items()})
    top = [w for w, _ in total.most_common(TOP_WORDS_PER_LANG)]
    if not top:
        return []
    labels = [f"{agg['gloss_of'][(lang, w)].most_common(1)[0][0]} ({w})" if lang != "en" else w for w in top]
    matrix = []
    for m in models:
        c = agg["cells"].get((m, lang))
        matrix.append([c["glosses"][w] / c["sense"] if _usable(c) else float("nan") for w in top])
    fig, ax = plt.subplots(figsize=(11, 4.2))
    im = _heatmap(ax, matrix, [_short(m) for m in models], labels, SEQUENTIAL, 0, 1)
    ax.set_title(f"[{lang}] share of on-subject responses using each concept — stem: "
                 f"{agg['stem'][lang]}", fontsize=9, color=INK, loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.025)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=7, colors=MUTED, length=0)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return list(zip(top, labels))


def plot_cross(agg: dict, models: list[str], langs: list[str], out: Path) -> list[str]:
    total = Counter()
    for c in agg["cells"].values():
        if _usable(c):
            total.update({k: v / c["sense"] for k, v in c["glosses"].items()})
    top = [g for g, _ in total.most_common(TOP_GLOSSES)]
    if not top:
        return []
    rows, matrix = [], []
    for l in langs:
        for m in models:
            c = agg["cells"].get((m, l))
            rows.append(f"{l} · {_short(m)}")
            matrix.append([c["glosses"][g] / c["sense"] if _usable(c) else float("nan") for g in top])
    fig, ax = plt.subplots(figsize=(12, 9))
    im = _heatmap(ax, matrix, rows, top, SEQUENTIAL, 0, 1)
    for boundary in range(len(models), len(rows), len(models)):
        ax.axhline(boundary - 0.5, color=MUTED, linewidth=1)
    ax.set_title(f"Cross-language: share of on-subject responses using each {agg['subject']} descriptor "
                 "(English gloss)",
                 fontsize=9, color=INK, loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.02)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=7, colors=MUTED, length=0)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    return top


def write_tables(agg: dict, models: list[str], langs: list[str], out_dir: Path) -> None:
    with (out_dir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "lang", "n", "lang_match_rate", "subject_sense_rate", "sense_n", "low_n",
                    *[f"type_{t}" for t in RESPONSE_TYPES],
                    "net_valence", "positive", "neutral", "negative", "unlabeled", "eastern", "western", "general"])
        for m in models:
            for l in langs:
                c = agg["cells"].get((m, l))
                if not c:
                    continue
                nv = _net_valence(c)
                w.writerow([m, l, c["n"], round(c["lang_match"] / c["n"], 3), round(c["sense"] / c["n"], 3),
                            c["sense"], not _usable(c),
                            *[c["types"][t] for t in RESPONSE_TYPES], "" if nv is None else round(nv, 3),
                            *[c["valence"][k] for k in ("positive", "neutral", "negative", "unlabeled")],
                            *[c["tradition"][k] for k in ("eastern", "western", "general")]])
    with (out_dir / "descriptors.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "lang", "concept", "top_native_lemma", "responses", "share_of_subject_sense"])
        for (m, l), c in sorted(agg["cells"].items()):
            for concept, n in c["glosses"].most_common():
                lemma = agg["gloss_of"][(l, concept)].most_common(1)[0][0]
                w.writerow([m, l, concept, lemma, n, round(n / c["sense"], 3) if c["sense"] else ""])


def write_markdown(agg: dict, models: list[str], langs: list[str], out_dir: Path) -> None:
    lines = [f"# Dragon Bench report: {agg['subject']}", "",
             "Stems: " + ", ".join(f"{l} `{agg['stem'][l]}`" for l in langs), "",
             f"Cells with fewer than {MIN_CELL_N} on-subject, same-language responses are marked *low n* and left out "
             "of the heatmaps.", "",
             "## Filtering funnel", "",
             "| model | lang | n | same language | on subject | clarification | multi_sense | definition | completion | net valence | eastern / western / general |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in models:
        for l in langs:
            c = agg["cells"].get((m, l))
            if not c:
                continue
            nv = _net_valence(c)
            t = c["tradition"]
            lines.append(
                f"| {_short(m)} | {l} | {c['n']} | {c['lang_match']} | {c['sense']} | {c['types']['clarification']} | "
                f"{c['types']['multi_sense']} | {c['types']['definition']} | {c['types']['completion']} | "
                f"{'' if nv is None else f'{nv:+.2f}'}{'' if _usable(c) else ' *low n*'} | "
                f"{t['eastern']} / {t['western']} / {t['general']} |")
    lines += ["", "## Top descriptors per cell (share of on-subject responses)", ""]
    for l in langs:
        lines += [f"### {l} `{agg['stem'][l]}`", ""]
        for m in models:
            c = agg["cells"].get((m, l))
            if not _usable(c):
                continue
            top = ", ".join(
                f"{w}{'' if l == 'en' else ' ' + agg['gloss_of'][(l, w)].most_common(1)[0][0]} {n / c['sense']:.0%}"
                for w, n in c["glosses"].most_common(10))
            lines.append(f"- **{_short(m)}** (n={c['sense']}): {top}")
        lines.append("")
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def report(run_dir: Path) -> None:
    rows, valence = load(run_dir)
    present_models = {r["model"] for r in rows}
    models = [m for m in MODELS if m in present_models] + sorted(present_models - set(MODELS))
    langs = [l for l in LANG_ORDER if any(r["lang"] == l for r in rows)]
    agg = aggregate(rows, valence)
    agg["stem"] = {r["lang"]: r["stem"] for r in rows}
    agg["subject"] = run_subject(run_dir).self_words[0]
    out_dir = run_dir / "report"
    out_dir.mkdir(exist_ok=True)
    plot_valence(agg, models, langs, out_dir / "valence.png")
    for l in langs:
        plot_words_by_lang(agg, models, l, out_dir / f"words_{l}.png")
    plot_cross(agg, models, langs, out_dir / "words_cross.png")
    write_tables(agg, models, langs, out_dir)
    write_markdown(agg, models, langs, out_dir)
    print(f"report written to {out_dir}")
