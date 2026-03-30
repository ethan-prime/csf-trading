from __future__ import annotations

from datetime import datetime, timedelta, timezone
import time
from typing import Any
from urllib.parse import quote

import requests

import config as cfg
from db.database import Database

DEFAULT_API_ROOT = "https://csfloat.com/api/v1"
API_ROOT = getattr(cfg, "API_URL", DEFAULT_API_ROOT).rstrip("/")
API_KEY = getattr(cfg, "API_KEY_CSF", "")
COOKIE = getattr(cfg, "COOKIE", "")
REQUEST_TIMEOUT_SECONDS = getattr(cfg, "REQUEST_TIMEOUT_SECONDS", 20)
MIN_REQUEST_INTERVAL_SECONDS = getattr(cfg, "MIN_REQUEST_INTERVAL_SECONDS", 0.35)
MAX_RETRIES = getattr(cfg, "MAX_RETRIES", 4)

JsonDict = dict[str, Any]

bids = Database("db/bids")
cache = Database("db/cache")
proxies = None

_session = requests.Session()
_last_request_ts = 0.0
_supports_history_sales: bool | None = None


def _default_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    if API_KEY:
        headers["Authorization"] = API_KEY
    if COOKIE:
        headers["Cookie"] = COOKIE if "=" in COOKIE else f"session={COOKIE}"
    return headers


def _throttle() -> None:
    global _last_request_ts

    elapsed = time.time() - _last_request_ts
    if elapsed < MIN_REQUEST_INTERVAL_SECONDS:
        time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)
    _last_request_ts = time.time()


def cooldown(seconds: int = 15 * 60) -> None:
    print(f"Rate-limited. Sleeping {seconds}s...")
    time.sleep(seconds)


def _decode_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return {}


def _request(method: str, path: str, *, params: JsonDict | None = None, json: JsonDict | None = None) -> Any:
    url = f"{API_ROOT}{path}"

    for attempt in range(MAX_RETRIES):
        _throttle()
        try:
            response = _session.request(
                method,
                url,
                headers=_default_headers(),
                params=params,
                json=json,
                proxies=proxies,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Network error while requesting {path}: {exc}") from exc
            time.sleep(min(30, 2**attempt))
            continue

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "")
            wait_seconds = int(retry_after) if retry_after.isdigit() else min(60, 2**attempt)

            if attempt == MAX_RETRIES - 1:
                cooldown(max(1, wait_seconds))
                raise RuntimeError("CSFloat rate limit exceeded after retries")

            time.sleep(max(1, wait_seconds))
            continue

        if response.status_code >= 400:
            body = response.text.strip()
            raise RuntimeError(f"CSFloat API error {response.status_code} at {path}: {body[:300]}")

        return _decode_json(response)

    raise RuntimeError(f"Failed to request {path}")


def _extract_data(payload: Any) -> list[JsonDict]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]

    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]

        results = payload.get("results")
        if isinstance(results, list):
            return [x for x in results if isinstance(x, dict)]

    return []


def _extract_orders(payload: Any) -> list[JsonDict]:
    if isinstance(payload, dict):
        orders = payload.get("orders")
        if isinstance(orders, list):
            return [x for x in orders if isinstance(x, dict)]
    return _extract_data(payload)


def sum_stickers(stickers: list[JsonDict]) -> int:
    total = 0
    for sticker in stickers:
        reference = sticker.get("reference") or {}
        scm = sticker.get("scm") or {}
        total += int(reference.get("price", scm.get("price", 0)))
    return total


# SALES

def _get_sales_from_history(item_name: str) -> list[JsonDict]:
    encoded_name = quote(item_name, safe="")
    payload = _request("GET", f"/history/{encoded_name}/sales")
    return _extract_data(payload)


def _get_sales_from_listing(listing_id: int | str) -> list[JsonDict]:
    payload = _request("GET", f"/listings/{listing_id}/sales")
    return _extract_data(payload)


def get_sales(item_name: str, sticker_price_threshold: int = 0, listing_id: int | str | None = None) -> list[JsonDict]:
    global _supports_history_sales

    sales: list[JsonDict] = []

    if _supports_history_sales is not False:
        try:
            sales = _get_sales_from_history(item_name)
            _supports_history_sales = True
        except RuntimeError:
            _supports_history_sales = False

    if not sales:
        if listing_id is None:
            _, _, listing_id, _ = get_info_by_hash_name(item_name)
        sales = _get_sales_from_listing(listing_id)

    filtered_sales: list[JsonDict] = []
    for sale in sales:
        stickers = sale.get("stickers")
        if not isinstance(stickers, list):
            filtered_sales.append(sale)
            continue
        if sum_stickers(stickers) <= sticker_price_threshold:
            filtered_sales.append(sale)

    return filtered_sales


def get_sales_prices(sales: list[JsonDict]) -> list[int]:
    prices: list[int] = []
    for sale in sales:
        if "price" in sale:
            prices.append(int(sale["price"]))
        elif "sale_price" in sale:
            prices.append(int(sale["sale_price"]))
    return prices


def get_base_price(listing_id: int | str) -> tuple[int, int]:
    listing = _request("GET", f"/listings/{listing_id}")
    reference = listing.get("reference", {}) if isinstance(listing, dict) else {}

    if isinstance(listing, dict):
        base_price = int(reference.get("base_price", listing.get("price", 0)))
    else:
        base_price = 0

    predicted_price = int(reference.get("predicted_price", base_price))
    return base_price, predicted_price


def get_info_by_hash_name(hash_name: str) -> tuple[int, int, int | str, str]:
    listings = get_listings_by_name(hash_name)
    if not listings:
        raise RuntimeError(f"No listing found for market_hash_name={hash_name}")

    first = listings[0]
    reference = first.get("reference", {})
    item = first.get("item", {})

    base_price = int(reference.get("base_price", first.get("price", 0)))
    predicted_price = int(reference.get("predicted_price", base_price))
    listing_id = first["id"]
    icon_url = str(item.get("icon_url", ""))

    return base_price, predicted_price, listing_id, icon_url


def avg(nums: list[int | float]) -> float:
    return sum(nums) / len(nums)


def to_usd(csf_price: int | float) -> float:
    return csf_price / 100


# BUY ORDERS

def get_buy_orders(listing_id: int | str, expect: str) -> list[JsonDict]:
    payload = _request("GET", f"/listings/{listing_id}/buy-orders", params={"limit": 20})
    buy_orders = [
        order
        for order in _extract_data(payload)
        if order.get("market_hash_name") == expect or order.get("expression") == expect
    ]
    buy_orders.sort(key=lambda x: int(x.get("price", 0)), reverse=True)
    return buy_orders


def get_max_buy_order(listing_id: int | str, item: str) -> int:
    orders = get_buy_orders(listing_id, item)
    if not orders:
        return 0
    return max(int(order.get("price", 0)) for order in orders)


def add_buy_order(max_price: int, quantity: int = 1, item_name: str | None = None, expression: str | None = None) -> None:
    bid_key = item_name or expression
    if bid_key is None:
        print("No item name or expression specified for buy order.")
        return

    if bid_key in bids.data:
        print(f"Buy order unsuccessful: already bidding on {bid_key}.")
        return

    payload: JsonDict = {"max_price": max_price, "quantity": quantity}
    if expression is not None:
        payload["expression"] = expression
    else:
        payload["market_hash_name"] = item_name

    try:
        _request("POST", "/buy-orders", json=payload)
    except RuntimeError as exc:
        print("Error submitting buy order...")
        print(exc)
        return

    print(f"Submitted buy order: {payload}")
    bids.add(bid_key, {"item": bid_key, "bid_price": max_price})


def remove_buy_order(order_id: int | str, item_name: str) -> None:
    try:
        _request("DELETE", f"/buy-orders/{order_id}")
    except RuntimeError as exc:
        print("Error removing buy order")
        print(exc)
        return

    print(f"Successfully removed buy order {order_id}")
    if item_name:
        bids.clear_section(item_name)


def get_my_buy_orders() -> JsonDict:
    payload = _request("GET", "/me/buy-orders", params={"page": 0, "limit": 100})
    orders = _extract_orders(payload)

    if isinstance(payload, dict):
        payload["orders"] = orders
        return payload

    return {"orders": orders}


# LISTINGS

def get_listings_by_name(hash_name: str) -> list[JsonDict]:
    payload = _request(
        "GET",
        "/listings",
        params={
            "market_hash_name": hash_name,
            "category": 1,
            "sort_by": "most_recent",
            "limit": 50,
        },
    )
    return _extract_data(payload)


def get_listings_by_price(min_price: int, max_price: int) -> list[JsonDict]:
    payload = _request(
        "GET",
        "/listings",
        params={
            "min_price": min_price * 100,
            "max_price": max_price * 100,
            "category": 1,
            "sort_by": "most_recent",
            "limit": 50,
        },
    )
    return _extract_data(payload)


def _parse_datetime(date_str: str) -> datetime:
    normalized = date_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass

    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue

    # Some payloads include more than 6 fractional digits; trim and retry.
    if "." in normalized and "+" in normalized:
        left, tz = normalized.rsplit("+", 1)
        base, frac = left.split(".", 1)
        frac = frac[:6]
        candidate = f"{base}.{frac}+{tz}"
        return datetime.strptime(candidate, "%Y-%m-%dT%H:%M:%S.%f%z")

    raise ValueError(f"Unsupported datetime format: {date_str}")


def was_recent(date_str: str, n_days: int) -> bool:
    date_obj = _parse_datetime(date_str)
    current_time = datetime.now(timezone.utc)
    return (current_time - date_obj) <= timedelta(days=n_days)


def volume(sales: list[JsonDict], n_days: int) -> int:
    def sale_time(sale: JsonDict) -> str | None:
        sold_at = sale.get("sold_at")
        if isinstance(sold_at, str):
            return sold_at

        created_at = sale.get("created_at")
        if isinstance(created_at, str):
            return created_at

        updated_at = sale.get("updated_at")
        if isinstance(updated_at, str):
            return updated_at

        return None

    count = 0
    for sale in sales:
        timestamp = sale_time(sale)
        if timestamp and was_recent(timestamp, n_days=n_days):
            count += 1
    return count


def has_volume(sales: list[JsonDict], n_sales: int, n_days: int) -> bool:
    return volume(sales, n_days) >= n_sales


def price_accurate(price: int, sale_prices: list[int], percent: float = 0.03, verbose: bool = False) -> bool:
    if not sale_prices:
        return False

    average = avg(sale_prices)
    if average - price >= 0:
        return True

    if verbose:
        print(f"avg: {average} | csf price: {price} | eq: {percent * price}")

    return (price - average) <= percent * price


def parse_args(raw: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for arg in raw.split():
        key, _, value = arg.partition("=")
        if key:
            parsed[key] = value
    return parsed
