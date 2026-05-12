import os
import time
import requests
from datetime import datetime

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL = "@thetopminers"  # این رو عوض کن به اسم کانالت

print("🚀 Bot is starting...")
print(f"Token exists: {BOT_TOKEN is not None}")
print(f"Channel: {CHANNEL}")

if not BOT_TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN not set!")
    exit(1)

def send_test_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL,
        "text": f"🟢 Bot is alive! {datetime.now()}",
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        print(f"Response: {r.status_code} - {r.text}")
        if r.status_code == 200:
            print("✅ Message sent!")
        else:
            print("❌ Failed to send")
    except Exception as e:
        print(f"❌ Error: {e}")

print("Sending test message...")
send_test_message()
print("Bot finished.")
