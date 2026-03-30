from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
import time
from collections import defaultdict
from statistics import mean
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config as cfg


def _headers() -> dict[str, str]:
    headers: dict[str, str] = {}

    api_key = getattr(cfg, "API_KEY_CSF", "")
    cookie = getattr(cfg, "COOKIE", "")

    if api_key:
        headers["Authorization"] = api_key
    if cookie:
        headers["Cookie"] = cookie if "=" in cookie else f"session={cookie}"

    return headers


def _fetch_listings(
    session: requests.Session,
    base_url: str,
    page: int,
    min_price: int,
    max_price: int,
    request_delay: float,
) -> list[dict[str, Any]]:
    params = {
        "min_price": min_price * 100,
        "max_price": max_price * 100,
        "category": 1,
        "sort_by": "most_recent",
        "limit": 50,
        "page": page,
    }

    for attempt in range(3):
        response = session.get(
            f"{base_url}/listings",
            params=params,
            headers=_headers(),
            timeout=20,
        )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "")
            wait = int(retry_after) if retry_after.isdigit() else 5 * (attempt + 1)
            print(f"Rate limited on page {page}, sleeping {wait}s...")
            time.sleep(wait)
            continue

        response.raise_for_status()
        payload = response.json()
        time.sleep(request_delay)

        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]

        if isinstance(payload, dict):
            data = payload.get("data", [])
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]

        return []

    return []


def scrape_newest(min_price: int, max_price: int, pages: int, request_delay: float) -> tuple[list[dict[str, Any]], list[str]]:
    base_url = getattr(cfg, "API_URL", "https://csfloat.com/api/v1").rstrip("/")
    session = requests.Session()

    by_name: dict[str, list[int]] = defaultdict(list)
    raw_count = 0

    for page in range(pages):
        listings = _fetch_listings(
            session=session,
            base_url=base_url,
            page=page,
            min_price=min_price,
            max_price=max_price,
            request_delay=request_delay,
        )

        if not listings:
            break

        for listing in listings:
            raw_count += 1
            item = listing.get("item", {})
            name = item.get("market_hash_name") or listing.get("market_hash_name")
            if not name:
                continue
            price = int(listing.get("price", 0))
            by_name[str(name)].append(price)

    rows: list[dict[str, Any]] = []
    for name, prices in by_name.items():
        rows.append(
            {
                "item_name": name,
                "listings_seen": len(prices),
                "min_price_usd": round(min(prices) / 100, 2),
                "avg_price_usd": round(mean(prices) / 100, 2),
                "max_price_usd": round(max(prices) / 100, 2),
            }
        )

    rows.sort(key=lambda row: (row["listings_seen"], -row["avg_price_usd"]), reverse=True)
    ordered_names = [row["item_name"] for row in rows]

    print(
        f"Scanned {raw_count} listings across {pages} page(s). "
        f"Found {len(ordered_names)} unique skins in ${min_price}-${max_price}."
    )

    return rows, ordered_names


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape newest CSFloat listings and rank skin candidates.")
    parser.add_argument("--min-price", type=int, default=10, help="Minimum price in USD (inclusive).")
    parser.add_argument("--max-price", type=int, default=500, help="Maximum price in USD (inclusive).")
    parser.add_argument("--pages", type=int, default=4, help="How many newest pages to scan (50 listings/page).")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in seconds.")
    parser.add_argument(
        "--out-csv",
        type=str,
        default="output/newest_10_500_candidates.csv",
        help="Output CSV path for scored candidates.",
    )
    parser.add_argument(
        "--out-list",
        type=str,
        default="output/newest_10_500_candidates.txt",
        help="Output text path with one skin per line.",
    )
    args = parser.parse_args()

    rows, ordered_names = scrape_newest(
        min_price=args.min_price,
        max_price=args.max_price,
        pages=args.pages,
        request_delay=args.delay,
    )

    with open(args.out_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["item_name", "listings_seen", "min_price_usd", "avg_price_usd", "max_price_usd"],
        )
        writer.writeheader()
        writer.writerows(rows)

    with open(args.out_list, "w", encoding="utf-8") as txtfile:
        txtfile.write("\n".join(ordered_names))
        txtfile.write("\n")

    print(f"Wrote {len(rows)} candidates to {args.out_csv} and {args.out_list}")


if __name__ == "__main__":
    main()
