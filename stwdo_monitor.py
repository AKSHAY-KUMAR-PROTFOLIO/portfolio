#!/usr/bin/env python3
from pathlib import Path
import os, sys, time, requests, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.stwdo.de/en/living-houses-application/current-housing-offers"
NO_RESULTS_PHRASE = "No results found for the given search criteria."
STATE_PATH = Path("state/status.txt")
USER_AGENT = "stwdo-monitor/1.1"

# --- Telegram notification ---
def notify_telegram(token: str, chat_id: str, text: str) -> bool:
    try:
        api = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(api, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[WARN] Telegram failed: {e}")
        return False

# --- Gmail notification with retry ---
def notify_gmail_until_success(sender: str, password: str, to: str, subject: str, body: str, max_attempts=15) -> bool:
    recipients = [email.strip() for email in to.split(",")]
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        try:
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

            print(f"[INFO] Gmail succeeded after {attempts} attempt(s).")
            return True

        except Exception as e:
            print(f"[WARN] Gmail attempt {attempts} failed: {e}")
            time.sleep(5)

    print("[ERROR] Gmail failed after all retries.")
    return False

# --- Fetch page ---
def fetch_page(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text

def offers_present(html: str) -> bool:
    return NO_RESULTS_PHRASE not in html

# --- State read/write ---
def read_state() -> str | None:
    if STATE_PATH.exists():
        return STATE_PATH.read_text().strip()
    return None

def write_state(value: str):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(value)

def main():
    try:
        html = fetch_page(URL)
    except Exception as e:
        print(f"[ERROR] Failed to fetch page: {e}")
        sys.exit(1)

    present = offers_present(html)
    prev = read_state()

    new_state = "offers" if present else "no_offers"
    print(f"[INFO] Previous state: {prev} -> New state: {new_state}")

    # Determine event type (edge-trigger only)
    should_notify = False
    event_type = None

    if prev is None:
        if present:
            should_notify = True
            event_type = "appeared"
    else:
        if prev == "no_offers" and present:
            should_notify = True
            event_type = "appeared"
        elif prev == "offers" and not present:
            should_notify = True
            event_type = "disappeared"

    if not should_notify:
        print("[INFO] No notification needed.")
        write_state(new_state)
        return

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if event_type == "appeared":
        msg = (
            "🏠 <b>New STWDO housing offers available!</b>\n"
            f"Time: {timestamp}\n"
            f"{URL}"
        )
    else:
        msg = (
            "🔒 <b>STWDO housing offers closed / disappeared.</b>\n"
            f"Time: {timestamp}\n"
            f"{URL}"
        )

    # Load secrets
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    gmail_addr = os.getenv("GMAIL_ADDRESS")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
    to_email = os.getenv("TO_EMAIL")

    sent_ok = False

    # Try Telegram once
    if tg_token and tg_chat_id:
        if notify_telegram(tg_token, tg_chat_id, msg):
            sent_ok = True

    # Gmail MUST succeed before updating state
    if gmail_addr and gmail_pass and to_email:
        if notify_gmail_until_success(gmail_addr, gmail_pass, to_email, "STWDO Update", msg):
            sent_ok = True

    if not sent_ok:
        print("[ERROR] No notification succeeded. NOT updating state.")
        sys.exit(2)

    write_state(new_state)
    print("[INFO] State updated.")

if __name__ == "__main__":
    main()
