import argparse
import asyncio

from .config import RUNS_DIR, SamplingParams


def main() -> None:
    parser = argparse.ArgumentParser(prog="dragon-bench")
    sub = parser.add_subparsers(dest="command", required=True)

    p_collect = sub.add_parser("collect", help="sample bare-stem responses from every model and language")
    p_collect.add_argument("run", help="run name under data/runs/")
    p_collect.add_argument("--samples", type=int, default=100)
    p_collect.add_argument("--models", nargs="*")
    p_collect.add_argument("--langs", nargs="*")

    p_extract = sub.add_parser("extract", help="filter responses and extract dragon descriptors")
    p_extract.add_argument("run")

    p_report = sub.add_parser("report", help="aggregate extractions into tables and heatmaps")
    p_report.add_argument("run")

    args = parser.parse_args()
    run_dir = RUNS_DIR / args.run

    if args.command == "collect":
        from .collect import collect

        defaults = SamplingParams()
        params = SamplingParams(
            samples=args.samples,
            models=args.models or defaults.models,
            langs=args.langs or defaults.langs,
        )
        asyncio.run(collect(run_dir, params))
    elif args.command == "extract":
        from .extract import extract

        asyncio.run(extract(run_dir))
    elif args.command == "report":
        from .report import report

        report(run_dir)
