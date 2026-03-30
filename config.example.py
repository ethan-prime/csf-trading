"""Copy to config.py and fill credentials."""

API_URL = "https://csfloat.com/api/v1"
API_KEY_CSF = ""
DISCORD_WEBHOOK_URL = ""

# Optional. If you use a session value only, either format works:
# COOKIE = "session=<value>" or COOKIE = "<value>"
COOKIE = ""

# Request tuning (kept conservative for CSFloat limits)
REQUEST_TIMEOUT_SECONDS = 20
MIN_REQUEST_INTERVAL_SECONDS = 0.35
MAX_RETRIES = 4
