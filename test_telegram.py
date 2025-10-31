#!/usr/bin/env python3
"""
Test Telegram bot message.
Sends a simple message to verify your token and chat ID.
"""

import os
import requests

# Get credentials from environment variables
token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

if not token or not chat_id:
    print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
    exit(1)

message = "✅ Test message from Telegram bot"

try:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": message})
    resp.raise_for_status()
    print("Message sent successfully!")
except Exception as e:
    print(f"Failed to send message: {e}")
