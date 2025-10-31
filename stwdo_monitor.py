# Replace nothing here — values are already filled for your repo
set -euo pipefail

GITHUB_USER="akshay-kumar-protfolio"
REPO_NAME="portfolio"
WORK_DIR="$HOME/${REPO_NAME}-bot-temp"

echo "==> Creating workspace at $WORK_DIR"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "==> Cloning your repo (read-only clone then push using your auth)"
git clone "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
cd "${REPO_NAME}"

# create bot folder
mkdir -p bot

cat > bot/stwdo_monitor.py <<'PY'
#!/usr/bin/env python3
"""
stwdo_monitor.py
Checks Studierendenwerk Dortmund current housing offers page and notifies via Telegram
Saves state in bot/state/status.txt (committed by GitHub Actions)
Requirements:
  pip install requests beautifulsoup4
Env:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""
from pathlib import Path
import os, sys, time, requests
from bs4 import BeautifulSoup

URL = "https://www.stwdo.de/en/living-houses-application/current-housing-offers"
NO_RESULTS_PHRASE = "No results found for the given search criteria."
STATE_PATH = Path("bot/state/status.txt")
USER_AGENT = "stwdo-monitor/1.0 (+https://github.com/you)"

def notify_telegram(token: str, chat_id: str, text: str) -> bool:
    try:
        api = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(api, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] Telegram notification failed: {e}", file=sys.stderr)
        return False

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

def offers_present(html: str) -> bool:
    return NO_RESULTS_PHRASE not in html

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

def extract_snippet(html: str, max_len: int = 800) -> str:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = "\n".join(lines)
    return joined[:max_len] + ("…" if len(joined) > max_len else "")

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
        token = os.getenv("8286447523:AAHJ91zoJ1qM9x6f4RhK_9ng6vJn6F1z_6U")
        chat_id = os.getenv("645607435")
        if not (token and chat_id):
            print("[WARN] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set; skipping notification.")
        else:
            snippet = extract_snippet(html, max_len=1200)
            message = (
                "🏠 STWDO — New housing offers detected!\n\n"
                f"URL: {URL}\n\n"
                "Snippet:\n" + snippet
            )
            ok = notify_telegram(token, chat_id, message)
            if ok:
                print("[INFO] Telegram notification sent.")
            else:
                print("[ERROR] Telegram notification failed; check logs.")
    else:
        print("[INFO] No notification necessary.")

    try:
        write_state(new_state)
    except Exception as e:
        print(f"[ERROR] Writing state failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
PY

cat > bot/requirements.txt <<'TXT'
requests
beautifulsoup4
TXT

# Create the workflow (placed in the repo's .github/workflows)
mkdir -p .github/workflows
cat > .github/workflows/stwdo.yml <<'YML'
name: STWDO Monitor

on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo (allow pushes)
        uses: actions/checkout@v4
        with:
          persist-credentials: true
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install -r bot/requirements.txt

      - name: Run monitor
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python3 bot/stwdo_monitor.py
          echo "Monitor finished."

      - name: Commit and push updated state (if any)
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          if git status --porcelain | grep -q "bot/state/status.txt"; then
            git add bot/state/status.txt
            git commit -m "Update monitor state [skip ci]"
            git push origin HEAD:main
          else
            echo "No state changes to commit."
          fi
YML

# Stage & commit changes
git add bot .github/workflows/stwdo.yml
git commit -m "Add STWDO monitor bot and GitHub Actions workflow" || true

# Push to origin (may require auth)
echo "==> Pushing changes to https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
git push origin HEAD:main

echo
echo "==> Files added under 'bot/' and workflow created at .github/workflows/stwdo.yml"
echo "==> Next: add your Telegram secrets so Actions can notify you."

echo
echo "To set Telegram secrets run (replace <token> and <chatid>):"
echo "  gh secret set TELEGRAM_BOT_TOKEN --body '<your-bot-token>' --repo ${GITHUB_USER}/${REPO_NAME}"
echo "  gh secret set TELEGRAM_CHAT_ID --body '<your-chat-id>' --repo ${GITHUB_USER}/${REPO_NAME}"
echo
echo "If 'gh' is not authenticated, run: gh auth login"
echo
echo "Then go to your repo → Actions → STWDO Monitor → Run workflow (manual) to test."

