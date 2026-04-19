import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from layer6_feedback.main import run_feedback_loop
from pipeline.orchestrator import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Small-cap investment pipeline")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--tickers",
        nargs="+",
        metavar="TICKER",
        help="Uruchom pipeline dla podanych tickerów",
    )
    group.add_argument(
        "--feedback",
        action="store_true",
        help="Uruchom tylko feedback loop (warstwa 6)",
    )
    args = parser.parse_args()

    if args.feedback:
        run_feedback_loop()
    elif args.tickers:
        run_pipeline(tickers=args.tickers)
    else:
        run_pipeline()


if __name__ == "__main__":
    main()
