#!/usr/bin/env python3
"""
stwdo_monitor.py
Checks Studierendenwerk Dortmund housing offers and notifies via Telegram + Gmail.
Requirements:
  pip install requests beautifulsoup4
Env (GitHub Actions secrets):
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
  GMAIL_ADDRESS
  GMAIL_APP_PASSWORD
  TO_EMAIL
"""
from pathlib import Path
import os, sys, time, requests, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# Constants
URL = "https://www.stwdo.de/en/living-houses-application/current-housing-offers"
NO_RESULTS_PHRASE = "No results found for the given search criteria."
STATE_PATH = Path("state/status.txt")
USER_AGENT = "stwdo-monitor/1.0 (+https://github.com/you)"

# --- Telegram notification ---
def notify_telegram(token: str, chat_id: str, text: str) -> bool:
    try:
        api = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(api, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] Telegram notification failed: {e}", file=sys.stderr)
        return False

# --- Gmail notification ---
def notify_gmail(sender: str, password: str, to: str, subject: str, body: str) -> bool:
    try:
        recipients = [email.strip() for email in to.split(",")]
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[ERROR] Gmail notification failed: {e}", file=sys.stderr)
        return False

# --- Fetch page ---
def fetch_page(url: str, retries: int = 2, backoff: float = 1.0) -> str:
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(1, retries + 2):
        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt <= retries:
                time.sleep(backoff * attempt)
                continue
            raise

# --- Check if offers present ---
def offers_present(html: str) -> bool:
    return NO_RESULTS_PHRASE not in html

# --- Read/Write state ---
def read_state() -> str | None:
    if not STATE_PATH.exists():
        return None
    try:
        return STATE_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        return None

def write_state(value: str) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(value, encoding="utf-8")

# --- Extract snippet ---
def extract_snippet(html: str, max_len: int = 800) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = "\n".join(lines)
    return joined[:max_len] + ("…" if len(joined) > max_len else "")

# --- Main ---
def main():
    try:
        html = fetch_page(URL)
    except Exception as e:
        print(f"[ERROR] Failed to fetch page: {e}", file=sys.stderr)
        sys.exit(1)

    present = offers_present(html)
    prev = read_state()
    prev_display = prev if prev is not None else "unknown"

    if prev is None:
        should_notify = present
    else:
        should_notify = (prev == "no_offers" and present)

    new_state = "offers" if present else "no_offers"
    print(f"[INFO] Previous state: {prev_display}  ->  New state: {new_state}")

    if should_notify:
        # Telegram
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Gmail
        gmail_address = os.getenv("GMAIL_ADDRESS")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        to_email = os.getenv("TO_EMAIL")

        snippet = extract_snippet(html, max_len=1200)
        message_text = (
            "🏠 STWDO — New housing offers detected!\n\n"
            f"URL: {URL}\n\n"
            "Snippet:\n" + snippet
        )

        # Send Telegram
        if tg_token and tg_chat_id:
            ok = notify_telegram(tg_token, tg_chat_id, message_text)
            print("[INFO] Telegram notification sent." if ok else "[ERROR] Telegram failed.")
        else:
            print("[WARN] Telegram credentials missing; skipping notification.")

        # Send Gmail
        if gmail_address and gmail_password and to_email:
            ok = notify_gmail(gmail_address, gmail_password, to_email, "STWDO Housing Update", message_text)
            print("[INFO] Gmail notification sent." if ok else "[ERROR] Gmail failed.")
        else:
            print("[WARN] Gmail credentials missing; skipping notification.")

    else:
        print("[INFO] No notification necessary.")

    try:
        write_state(new_state)
    except Exception as e:
        print(f"[ERROR] Writing state failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
