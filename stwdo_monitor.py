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
    except:
        return False

# --- Gmail notification with retry until success ---
def notify_gmail_until_success(sender: str, password: str, to: str, subject: str, body: str, max_attempts=10) -> bool:
    attempts = 0
    recipients = [email.strip() for email in to.split(",")]

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

            print(f"[INFO] Gmail success after {attempts} attempt(s)")
            return True

        except Exception as e:
            print(f"[WARN] Gmail attempt {attempts} failed: {e}")
            time.sleep(5)  # wait before retrying

    print("[ERROR] Gmail never succeeded after all retries.")
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

# --- Extract snippet ---
def extract_snippet(html: str, max_len=800) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n").strip()
    text = "\n".join([ln.strip() for ln in text.splitlines() if ln.strip()])
    return text[:max_len] + ("…" if len(text) > max_len else "")

def main():
    try:
        html = fetch_page(URL)
    except Exception as e:
        print(f"[ERROR] Failed to fetch page: {e}")
        sys.exit(1)

    present = offers_present(html)
    prev = read_state()

    new_state = "offers" if present else "no_offers"

    print(f"[INFO] Previous: {prev} → New: {new_state}")

    # Determine if we should notify (edge triggers)
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

    # Prepare content
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if event_type == "appeared":
        msg = (
            "🏠 <b>New STWDO housing offers available!</b>\n\n"
            f"URL: {URL}\n"
            f"Time: {timestamp}\n\n"
            + extract_snippet(html, 1200)
        )
    else:
        msg = (
            "🔒 <b>All STWDO housing offers have disappeared.</b>\n\n"
            f"URL: {URL}\n"
            f"Time: {timestamp}\n"
            f"No offers are currently listed."
        )

    # Load secrets
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    gmail_addr = os.getenv("GMAIL_ADDRESS")
    gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
    to_email = os.getenv("TO_EMAIL")

    sent_ok = False

    # Try Telegram first (one attempt)
    if tg_token and tg_chat_id:
        if notify_telegram(tg_token, tg_chat_id, msg):
            print("[INFO] Telegram OK")
            sent_ok = True
        else:
            print("[WARN] Telegram failed")

    # Gmail: retry until success
    if gmail_addr and gmail_pass and to_email:
        if notify_gmail_until_success(gmail_addr, gmail_pass, to_email, "STWDO Update", msg):
            sent_ok = True
    else:
        print("[WARN] Gmail disabled")

    if not sent_ok:
        print("[ERROR] No notification channel succeeded. State NOT updated.")
        sys.exit(2)

    # Only here → notifications succeeded
    write_state(new_state)
    print("[INFO] State updated successfully.")

if __name__ == "__main__":
    main()
