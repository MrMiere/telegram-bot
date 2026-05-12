import os
import time
import threading
import requests
import yfinance as yf
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set!")

CHANNEL = "@thetopminers"
HEALTH_PORT = int(os.environ.get("PORT", 8080))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        pass


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


def start_health_server():
    server = ReusableHTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
    print(f"✅ Health server on port {HEALTH_PORT}")
    server.serve_forever()


def send_to_channel(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHANNEL, "text": text, "parse_mode": "HTML"}, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Telegram API error: {r.text[:100]}")
    except Exception as e:
        print(f"❌ Send error: {e}")


def get_crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum,the-open-network", "vs_currencies": "usd"}
    try:
        data = requests.get(url, params=params, timeout=10).json()
        return {
            "BTC": round(data["bitcoin"]["usd"], 2),
            "ETH": round(data["ethereum"]["usd"], 2),
            "TON": round(data["the-open-network"]["usd"], 4),
        }
    except Exception as e:
        print(f"❌ Crypto API error: {e}")
        return None


def get_market():
    symbols = {"GOLD": "GC=F", "DXY": "DX-Y.NYB", "BRENT": "BZ=F", "WTI": "CL=F", "SP500": "^GSPC"}
    result = {}
    try:
        for name, symbol in symbols.items():
            ticker = yf.Ticker(symbol)
            price = ticker.fast_info.get("last_price", 0)
            result[name] = round(price, 2) if price else 0
        return result
    except Exception as e:
        print(f"❌ Market API error: {e}")
        return None


def build_message(crypto, market):
    if not crypto or not market:
        return None
    
    return (
        "<b>📡 LIVE MARKET ALERT</b>\n\n"
        f"🥇 Gold     → ${market.get('GOLD', 0):,.1f}\n"
        f"💵 DXY      → {market.get('DXY', 0):.2f}\n\n"
        f"₿ BTC       → ${crypto.get('BTC', 0):,.0f}\n"
        f"⟠ ETH       → ${crypto.get('ETH', 0):,.0f}\n"
        f"💎 TON      → ${crypto.get('TON', 0):.4f}\n\n"
        f"🛢️ Brent    → ${market.get('BRENT', 0):.2f}\n"
        f"🛢️ WTI      → ${market.get('WTI', 0):.2f}\n"
        f"📈 S&P500   → {market.get('SP500', 0):,.0f}\n\n"
        f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"<i>Live Market Alert</i>"
    )


def run():
    print("🚀 Live Market Bot Starting...")
    print(f"Channel: {CHANNEL}")
    print(f"Token exists: {bool(BOT_TOKEN)}")
    
    # اجرای health server در ترد جداگانه
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    time.sleep(2)
    print("✅ Health server started")
    
    print("🚀 Bot main loop started...")
    print("⏳ Waiting 10 seconds before first update...")
    time.sleep(10)
    
    counter = 0
    while True:
        try:
            print(f"\n📊 Update #{counter + 1} - {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")
            
            crypto = get_crypto()
            market = get_market()
            
            if crypto and market:
                msg = build_message(crypto, market)
                if msg:
                    send_to_channel(msg)
                    print("✅ Successfully sent to channel")
                else:
                    print("❌ Failed to build message")
            else:
                print("❌ Failed to fetch data")
            
            counter += 1
            
        except Exception as e:
            print(f"❌ Main loop error: {e}")
        
        time.sleep(600)  # 10 دقیقه


if __name__ == "__main__":
    run()
