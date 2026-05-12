import os
import time
import threading
import requests
import yfinance as yf
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@thetopminers"
HEALTH_PORT = int(os.environ.get("PORT", 8082))


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
    requests.post(url, data={"chat_id": CHANNEL, "text": text, "parse_mode": "HTML"}, timeout=10)


def get_crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum,the-open-network", "vs_currencies": "usd"}
    data = requests.get(url, params=params, timeout=10).json()
    return {
        "BTC": round(data["bitcoin"]["usd"], 2),
        "ETH": round(data["ethereum"]["usd"], 2),
        "TON": round(data["the-open-network"]["usd"], 4),
    }


def get_index(symbol):
    ticker = yf.Ticker(symbol)
    price = ticker.fast_info["last_price"]
    return round(price, 2)


def get_market():
    return {
        "GOLD": get_index("GC=F"),
        "DXY": get_index("DX-Y.NYB"),
        "BRENT": get_index("BZ=F"),
        "WTI": get_index("CL=F"),
        "SP500": get_index("^GSPC"),
    }


def build_message(c, m):
    return (
        "<b>📡 LIVE MARKET ALERT\n\n"
        f"🥇 Gold     → ${m['GOLD']:,.1f}\n"
        f"💵 DXY      → {m['DXY']:.2f}\n\n"
        f" ₿    BTC     → ${c['BTC']:,.0f}\n"
        f" ⟠    ETH     → ${c['ETH']:,.0f}\n"
        f"💎 TON      → ${c['TON']:.2f}\n\n"
        f"🛢️ Brent    → ${m['BRENT']:.2f}\n"
        f"🛢️ WTI       → ${m['WTI']:.2f}\n"
        f"📈 S&P500   → {m['SP500']:,.0f}\n\n"
        f"🕐 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</b>"
    )


def run():
    print("🚀 Live Market Bot Running...")

    threading.Thread(target=start_health_server, daemon=True).start()

    while True:
        try:
            crypto = get_crypto()
            market = get_market()
            msg = build_message(crypto, market)
            send_to_channel(msg)
            print("✅ Sent to channel")
        except Exception as e:
            print("❌ Error:", e)

        time.sleep(600)


if __name__ == "__main__":
    run()
