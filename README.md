# CSFloat Trading Bot

Automated tooling for scanning CSFloat listings, generating trade leads, and maintaining buy-order strategies.

## Features

- Scan a list of skins and score opportunities by EV + volume/sales heuristics.
- Send Discord alerts for qualified opportunities.
- Manage/reprice existing buy orders (`autobid`).
- Scrape and build candidate skin lists from newest CSFloat listings.
- Simple Flask dashboard for viewing local bid state.

## Requirements

- Python 3.10+
- Install dependencies (recommended in a virtualenv):

```bash
pip install requests numpy flask discord-webhook selenium tqdm
```

For `scraper/price_scraping.py`, you also need a Chrome/Chromium webdriver.

## Configuration

Create `config.py` (or copy from `config.example.py`):

```python
API_URL = "https://csfloat.com/api/v1"
API_KEY_CSF = "YOUR_CSFLOAT_API_KEY"
COOKIE = ""  # optional ("session=..." or raw session value)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

REQUEST_TIMEOUT_SECONDS = 20
MIN_REQUEST_INTERVAL_SECONDS = 0.35
MAX_RETRIES = 4
```

Important:

- `config.py` is gitignored.
- Treat `API_KEY_CSF` as secret.

## Primary Usage

### 1) Build/refresh candidate list from newest listings

```bash
python3 scraper/newest_market_scrape.py \
  --min-price 10 \
  --max-price 500 \
  --pages 6 \
  --delay 0.6 \
  --out-csv output/newest_10_500_candidates.csv \
  --out-list output/newest_10_500_candidates.txt
```

### 2) Run screener (single pass)

```bash
python3 screen.py input=output/newest_10_500_candidates.txt output=output/hits.csv
```

### 3) Run screener continuously

```bash
while true; do
  python3 -u screen.py input=output/newest_10_500_candidates.txt output=output/hits.csv
  sleep 30
done
```

### 4) Run autobid manager (live)

`bid.py` currently runs:

```python
autobid(threshold=0.045, delay=120)
```

Start it with:

```bash
python3 -u bid.py
```

### 5) Run autobid in safe dry-run mode (no buy/cancel actions)

```bash
python3 -u -c "from autobid.bidtools import autobid; autobid(threshold=0.045, delay=1, max_cycles=1, dry_run=True)"
```

## Fully Autonomous (tmux)

```bash
mkdir -p logs output

# Screener loop
tmux new -d -s csf_screener 'cd /home/ethan/code/csf-trading && while true; do python3 -u screen.py input=output/newest_10_500_candidates.txt output=output/hits.csv; sleep 30; done | tee -a logs/screener.log'

# Autobid loop
tmux new -d -s csf_autobid 'cd /home/ethan/code/csf-trading && while true; do python3 -u bid.py; sleep 5; done | tee -a logs/autobid.log'

# Check
tmux ls
```

Stop:

```bash
tmux kill-session -t csf_screener
tmux kill-session -t csf_autobid
```

## File-by-File Usage Reference

- `screen.py`: CLI entrypoint for screener.
  - Usage: `python3 screen.py input=<path> [output=<path>] [start=<index>]`
- `screener.py`: `Screener` class (loads item list, executes strategy loop).
- `screener_config.py`: Default screening thresholds and heuristic selection.
- `strategy/ArbitrageStrategy.py`: Core opportunity logic and alert trigger conditions.
- `tools.py`: CSFloat API client helpers, retries/rate-limit handling, listing/sales/order functions.
- `autobid/bidtools.py`: Buy-order maintenance logic.
  - Key functions: `autobid(...)`, `try_update_buy_order(...)`, dry-run support.
- `bid.py`: Autobid runner script (currently live mode).
- `visual.py`: Discord webhook helpers (`send_webhook`, `send_webhook_msg`).
- `stats.py`: Outlier removal helper (`remove_outliers_iqr`).
- `heuristics/harvey.py`: Heuristic scoring functions (`harvey`, `hamilton`).
- `scraper/newest_market_scrape.py`: Pull newest CSFloat listings and generate candidate files.
- `scraper/price_scraping.py`: Selenium scraper for csgoskins.gg pricing by skin list.
- `scrape.py`: Simple runner for `price_scraping.py` (expects `data/relevant_skins.txt`).
- `dashboard.py`: Flask app exposing local bid state.
  - Run: `python3 dashboard.py` then open `http://127.0.0.1:5000`
- `templates/index.html`: Dashboard template.
- `db/database.py`: Lightweight JSON-backed local datastore utility.
- `clear_db.py`: Clears local cache DB (`db/cache`).
- `config.example.py`: Example configuration template.
- `autobid/orders.txt`: Scratch/notes file (not required by runtime).
- `bids.json`: Legacy/placeholder JSON file.
- `db/cache`: Local cache store file.

## Operational Notes

- CSFloat API can rate-limit aggressively. Keep request delay conservative.
- If you see repeated 429s, increase delays and reduce candidate set size.
- `send_alert=True` sends Discord notifications but does not buy by itself.
- Buy placement happens through `add_buy_order` paths (primarily autobid logic).
