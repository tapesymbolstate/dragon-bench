import csv
import json
from collections import defaultdict
from pathlib import Path

from .config import RUNS_DIR, run_subject
from .report import DIVERGING, INK, LANG_ORDER, MUTED, SEQUENTIAL, _heatmap, plt

TOP_CONCEPTS = 6


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def overview(run_dirs: list[Path]) -> None:
    out_dir = RUNS_DIR.parent / "overview"
    out_dir.mkdir(exist_ok=True)
    rows, valence, eastern, western, n_models, top, stems = [], {}, {}, {}, {}, {}, {}
    for run_dir in run_dirs:
        label = f"{run_subject(run_dir).name} ({run_dir.name})"
        rows.append(label)
        stems[label] = json.loads((run_dir / "params.json").read_text(encoding="utf-8"))["stems"]
        shares: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        usable: dict[str, set[str]] = defaultdict(set)
        for s in _read_csv(run_dir / "report" / "summary.csv"):
            if s["low_n"] == "True" or not s["net_valence"]:
                continue
            usable[s["lang"]].add(s["model"])
            valence.setdefault((label, s["lang"]), []).append(float(s["net_valence"]))
            traditions = [int(s[k]) for k in ("eastern", "western", "general")]
            if sum(traditions):
                eastern.setdefault((label, s["lang"]), []).append(traditions[0] / sum(traditions))
                western.setdefault((label, s["lang"]), []).append(traditions[1] / sum(traditions))
        for lang, models in usable.items():
            n_models[(label, lang)] = len(models)
        # Mean over models of each concept's share, so every model weighs the same.
        for d in _read_csv(run_dir / "report" / "descriptors.csv"):
            if d["model"] in usable[d["lang"]] and d["share_of_subject_sense"]:
                shares[d["lang"]][f"{d['concept']} {d['top_native_lemma']}" if d["lang"] != "en" else d["concept"]] \
                    .append(float(d["share_of_subject_sense"]))
        for lang, by_concept in shares.items():
            k = len(usable[lang])
            ranked = sorted(by_concept.items(), key=lambda kv: -sum(kv[1]) / k)
            top[(label, lang)] = [(c, sum(v) / k) for c, v in ranked[:TOP_CONCEPTS]]

    langs = [l for l in LANG_ORDER if any((r, l) in valence for r in rows)]
    nan = float("nan")
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 0.45 * len(rows) + 1.6))
    v_matrix = [[_mean(valence.get((r, l), [])) if (r, l) in valence else nan for l in langs] for r in rows]
    e_matrix = [[_mean(eastern.get((r, l), [])) if (r, l) in eastern else nan for l in langs] for r in rows]
    for ax, matrix, cmap, vmin, vmax, fmt, title in [
        (axes[0], v_matrix, DIVERGING, -1, 1, "{:+.2f}", "Net valence (mean over models)"),
        (axes[1], e_matrix, SEQUENTIAL, 0, 1, "{:.0%}", "Descriptors attributed to East Asian tradition"),
    ]:
        _heatmap(ax, matrix, rows, langs, cmap, vmin, vmax, annotate=True, fmt=fmt)
        ax.xaxis.tick_top()
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
        ax.set_title(title, fontsize=9, color=INK, pad=20)
    axes[1].set_yticklabels([])
    fig.text(0.01, 0.01, "Low-n cells are left out; each model counts once per cell.", fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out_dir / "overview.png", dpi=180)
    plt.close(fig)

    lines = ["# Dragon Bench overview", "",
             "Net valence and tradition shares are means over the models whose cell is not low-n; "
             "concept shares are the mean share of on-subject responses that use the concept.", "",
             "| subject (run) | lang | stem | models | net valence (min … max) | eastern | western | top concepts |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        for l in langs:
            if (r, l) not in valence:
                continue
            vs = valence[(r, l)]
            concepts = ", ".join(f"{c} {s:.0%}" for c, s in top.get((r, l), []))
            lines.append(f"| {r} | {l} | `{stems[r][l]}` | {n_models[(r, l)]} | {_mean(vs):+.2f} "
                         f"({min(vs):+.2f} … {max(vs):+.2f}) | {_mean(eastern.get((r, l), [])):.0%} | "
                         f"{_mean(western.get((r, l), [])):.0%} | {concepts} |")
    (out_dir / "overview.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"overview written to {out_dir}")
