from __future__ import annotations

import numpy as np


def remove_outliers_iqr(prices: list[int] | list[float]) -> list[int | float]:
    if not prices:
        return []

    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return [price for price in prices if lower_bound <= price <= upper_bound]
