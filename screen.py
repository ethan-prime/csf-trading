from __future__ import annotations

import argparse
from pathlib import Path

from screener import Screener
from screener_config import (
    AUTOBID_EV_THRESHOLD,
    DELAY,
    DELTA,
    EPSILON,
    EV_THRESHOLD,
    HEURISTIC,
    MAX_PRICE,
    MIN_PRICE,
    MIN_SIMILAR_SALES,
    MIN_VOL,
    SEND_ALERT,
    STICKER_PRICE_THRESHOLD,
)
from strategy.ArbitrageStrategy import ArbitrageStrategy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run CSFloat screener against an item list.")

    parser.add_argument("--input", required=True, help="Input text file path, one skin per line.")
    parser.add_argument("--output", default="", help="Output CSV path. Defaults to output/<input filename>.")
    parser.add_argument("--start-at", type=int, default=0, help="Start index in input list.")
    parser.add_argument("--n-iters", type=int, default=1, help="How many full passes to run.")
    parser.add_argument("--loop-delay", type=int, default=0, help="Delay in seconds between passes.")

    parser.add_argument("--threshold", type=float, default=EV_THRESHOLD)
    parser.add_argument("--autobid-ev-threshold", type=float, default=AUTOBID_EV_THRESHOLD)
    parser.add_argument("--min-price", type=int, default=MIN_PRICE)
    parser.add_argument("--max-price", type=int, default=MAX_PRICE)
    parser.add_argument("--delta", type=float, default=DELTA)
    parser.add_argument("--epsilon", type=int, default=EPSILON)
    parser.add_argument("--strategy-delay", type=int, default=DELAY, help="Delay between each item evaluation.")
    parser.add_argument("--min-similar-sales", type=int, default=MIN_SIMILAR_SALES)
    parser.add_argument("--min-vol", type=int, default=MIN_VOL)
    parser.add_argument("--sticker-price-threshold", type=int, default=STICKER_PRICE_THRESHOLD)

    parser.add_argument(
        "--send-alert",
        action=argparse.BooleanOptionalAction,
        default=SEND_ALERT,
        help="Enable/disable Discord alerts.",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_file = args.input
    output_file = args.output or f"output/{Path(input_file).name}"

    screener = Screener(
        input_file,
        ArbitrageStrategy,
        min_price=args.min_price,
        max_price=args.max_price,
        threshold=args.threshold,
        delta=args.delta,
        epsilon=args.epsilon,
        delay=args.strategy_delay,
        min_similar_sales=args.min_similar_sales,
        min_vol=args.min_vol,
        heuristic=HEURISTIC,
        write_to_output=output_file,
        send_alert=args.send_alert,
        autobid_ev_threshold=args.autobid_ev_threshold,
        sticker_price_threshold=args.sticker_price_threshold,
    )
    screener.execute(n_iters=args.n_iters, delay=args.loop_delay, start_at=args.start_at)


if __name__ == "__main__":
    main()
