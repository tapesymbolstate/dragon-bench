import argparse
import asyncio

from .config import MODELS, RUNS_DIR, SUBJECTS, SamplingParams


def main() -> None:
    parser = argparse.ArgumentParser(prog="dragon-bench")
    sub = parser.add_subparsers(dest="command", required=True)

    p_collect = sub.add_parser("collect", help="sample bare-stem responses from every model and language")
    p_collect.add_argument("run", help="run name under data/runs/")
    p_collect.add_argument("--subject", choices=sorted(SUBJECTS), default="dragon")
    p_collect.add_argument("--samples", type=int, default=100)
    p_collect.add_argument("--models", nargs="*")
    p_collect.add_argument("--langs", nargs="*")

    p_extract = sub.add_parser("extract", help="filter responses and extract descriptors of the subject")
    p_extract.add_argument("run")

    p_report = sub.add_parser("report", help="aggregate extractions into tables and heatmaps")
    p_report.add_argument("run")

    p_sample = sub.add_parser("validation-sample", help="draw a stratified sample of responses to label by hand")
    p_sample.add_argument("run")
    p_sample.add_argument("--per-cell", type=int, default=2)

    p_validate = sub.add_parser("validate", help="compare hand labels with the extractor")
    p_validate.add_argument("run")

    p_overview = sub.add_parser("overview", help="compare net valence and tradition split across runs")
    p_overview.add_argument("runs", nargs="+")

    args = parser.parse_args()

    if args.command == "collect":
        from .collect import collect

        params = SamplingParams(
            subject=args.subject,
            samples=args.samples,
            models=args.models or list(MODELS),
            langs=args.langs or list(SUBJECTS[args.subject].stems),
        )
        asyncio.run(collect(RUNS_DIR / args.run, params))
    elif args.command == "extract":
        from .extract import extract

        asyncio.run(extract(RUNS_DIR / args.run))
    elif args.command == "report":
        from .report import report

        report(RUNS_DIR / args.run)
    elif args.command == "validation-sample":
        from .validate import draw_sample

        draw_sample(RUNS_DIR / args.run, args.per_cell)
    elif args.command == "validate":
        from .validate import validate

        validate(RUNS_DIR / args.run)
    elif args.command == "overview":
        from .overview import overview

        overview([RUNS_DIR / r for r in args.runs])
