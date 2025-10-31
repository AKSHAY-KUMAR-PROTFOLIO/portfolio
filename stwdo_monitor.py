#!/usr/bin/env python3
"""
stwdo_monitor.py
Checks Studierendenwerk Dortmund current housing offers page and notifies via Telegram.
Saves state in bot/state/status.txt (committed by GitHub Actions).

Requirements:
  pip install requests beautifulsoup4

Environment variables (set in GitHub Secrets):
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""

from pathlib import Path
import os
import sys
import time
import random
import requests
from bs4 import BeautifulSoup

# === CONFIG ===
URL = "https://www.stwdo.de/en/living-houses-application/current-housing-offers"
NO_RESULTS_PHRASE = "No results found for the given search criteria."
STATE_PATH = Path("bot/state/status.txt")
USER_AGENT = "stwdo-monitor/1.0 (+https://github.com/akshay-kumar-protfolio/portfolio)"


# === TELEGRAM ===
def notify_telegram(token: str, chat_id: str, text: str) -> bool:
    """Send a Telegram message."""
    try:
        api = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(
            api,
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] Telegram notification failed: {e}", file=sys.stderr)
        return False


# === FETCHING ===
def fetch_page(url: str, retries: int = 2, backoff: float = 1.0) -> str:
    """Fetch page with retries."""
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(1, retries + 2):
        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt <= retries:
                wait = backoff * attempt
                print(f"[WARN] Fetch failed ({e}); retrying in {wait:.1f}s...")
                time.sleep(wait)
                continue
            raise


# === PARSING ===
def offers_present(html: str) -> bool:
    """Return True if offers exist."""
    return NO_RESULTS_PHRASE not in html


def extract_snippet(html: str, max_len: int = 800) -> str:
    """Extract plain text snippet for Telegram message."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = "\n".join(lines)
    return joined[:max_len] + ("…" if len(joined) > max_len else "")


# === STATE ===
def read_state() -> str | None:
    """Read previous state (offers/no_offers)."""
    if not STATE_PATH.exists():
        return None
    try:
        return STATE_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        return None


def write_state(value: str) -> None:
    """Write new state."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(value, encoding="utf-8")


# === MAIN ===
def main():
    print("[INFO] Starting STWDO monitor...")
    # Add random small delay to avoid exact timing overlap
    time.sleep(random.uniform(1, 10))

    try:
        html = fetch_page(URL)
    except Exception as e:
        print(f"[ERROR] Failed to fetch page: {e}", file=sys.stderr)
        sys.exit(1)

    present = offers_present(html)
    prev = read_state()
    prev_display = prev if prev is not None else "unknown"
    new_state = "offers" if present else "no_offers"

    print(f"[INFO] Previous state: {prev_display}  ->  New state: {new_state}")

    # Decide whether to notify
    if prev is None:
        should_notify = present
    else:
        should_notify = (prev == "no_offers" and present)

    if should_notify:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not (token and chat_id):
            print("[WARN] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set; skipping notification.")
        else:
            snippet = extract_snippet(html, max_len=1200)
            message = (
                "🏠 <b>STWDO — New housing offers detected!</b>\n\n"
                f"🔗 URL: {URL}\n\n"
                f"📰 Snippet:\n{snippet}"
            )
            ok = notify_telegram(token, chat_id, message)
            if ok:
                print("[INFO] Telegram notification sent successfully.")
            else:
                print("[ERROR] Telegram notification failed; check logs.")
    else:
        print("[INFO] No new offers; nothing to notify.")

    # Update local state
    try:
        write_state(new_state)
        print("[INFO] State updated successfully.")
    except Exception as e:
        print(f"[ERROR] Writing state failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
