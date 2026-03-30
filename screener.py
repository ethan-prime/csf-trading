from __future__ import annotations

import time
from typing import Any, Callable

StrategyFn = Callable[..., Any]


class Screener:
    def __init__(self, scan_list: str, strategy: StrategyFn, **strategy_kwargs: Any) -> None:
        self.scan_list_path = scan_list
        self.strategy = strategy
        self.strategy_kwargs = strategy_kwargs
        self.items: list[str] = []

    def read_list(self) -> list[str]:
        with open(self.scan_list_path, "r", encoding="utf-8") as file:
            self.items = [line.strip() for line in file if line.strip()]
        return self.items

    def execute(self, n_iters: int = 1, delay: int = 0, start_at: int = 0) -> None:
        items = self.read_list()

        for _ in range(n_iters):
            print("Starting ArbitrageStrategy...")
            self.strategy(items[start_at:], **self.strategy_kwargs)
            time.sleep(delay)
