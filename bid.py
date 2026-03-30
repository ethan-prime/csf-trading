from __future__ import annotations

import argparse

from autobid.bidtools import autobid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run autobid manager.")
    parser.add_argument("--threshold", type=float, default=0.045, help="Bid threshold ratio.")
    parser.add_argument("--delay", type=int, default=120, help="Delay (seconds) between per-order actions.")
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="How many outer loops to run. Omit for infinite.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not place/cancel any orders.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    autobid(
        threshold=args.threshold,
        delay=args.delay,
        max_cycles=args.max_cycles,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
