import os
import json
import csv
import uuid
import time
import threading
from datetime import datetime, timezone

import websocket


API_KEY = os.getenv("INFOWAY_API_KEY")

if not API_KEY:
    print("ERROR: INFOWAY_API_KEY is not set")
    raise SystemExit(1)


URL = f"wss://data.infoway.io/ws?business=common&apikey={API_KEY}"

CSV_FILE = "infoway_USOIL_trades.csv"

HEARTBEAT_SECONDS = 30
RECONNECT_SECONDS = 5


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            writer.writerow([
                "received_timestamp",
                "source_timestamp",
                "symbol",
                "price",
                "volume",
                "td",
            ])


def save_trade(data):
    received = utc_now()

    source_ts = data.get("t")
    symbol = data.get("s")
    price = data.get("p")
    volume = data.get("v")
    td = data.get("td")

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            received,
            source_ts,
            symbol,
            price,
            volume,
            td,
        ])

    print(
        f"{received} | "
        f"source={source_ts} | "
        f"{symbol} | "
        f"PRICE={price} | "
        f"VOL={volume}"
    )


def send_heartbeat(ws):
    while ws.keep_running:
        time.sleep(HEARTBEAT_SECONDS)

        if not ws.keep_running:
            break

        try:
            heartbeat = {
                "code": 10010,
                "trace": str(uuid.uuid4())
            }

            ws.send(json.dumps(heartbeat))

            print(
                f"{utc_now()} | HEARTBEAT"
            )

        except Exception as e:
            print("HEARTBEAT ERROR:", e)
            break


def on_open(ws):
    print()
    print("=" * 60)
    print("CONNECTED")
    print("=" * 60)

    request = {
        "code": 10000,
        "trace": str(uuid.uuid4()),
        "data": {
            "codes": "USOIL"
        }
    }

    ws.send(json.dumps(request))

    print("SUBSCRIBED: USOIL")
    print(f"Saving trades to: {CSV_FILE}")

    heartbeat_thread = threading.Thread(
        target=send_heartbeat,
        args=(ws,),
        daemon=True
    )

    heartbeat_thread.start()


def on_message(ws, message):
    try:
        data = json.loads(message)

        code = data.get("code")

        if code == 200:
            print("SERVER:", data.get("msg"))

        elif code == 10001:
            print("SUBSCRIPTION:", data.get("msg"))

        elif code == 10002:
            trade = data.get("data")

            if trade:
                save_trade(trade)

        elif code == 10010:
            print(
                f"{utc_now()} | HEARTBEAT RESPONSE"
            )

        else:
            print(
                f"{utc_now()} | MESSAGE:",
                data
            )

    except Exception as e:
        print("MESSAGE ERROR:", e)


def on_error(ws, error):
    print()
    print("WEBSOCKET ERROR:", error)


def on_close(ws, close_status_code, close_msg):
    print()
    print(
        f"WEBSOCKET CLOSED: "
        f"code={close_status_code}, "
        f"msg={close_msg}"
    )


ensure_csv()

print("Starting Infoway USOIL collector...")
print("Automatic reconnect: ON")
print("Heartbeat: every 30 seconds")
print()


while True:

    try:

        ws = websocket.WebSocketApp(
            URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        ws.run_forever(
            ping_interval=None
        )

    except KeyboardInterrupt:
        print()
        print("Collector stopped by user.")
        break

    except Exception as e:
        print("CONNECTION ERROR:", e)

    print(
        f"Reconnecting in {RECONNECT_SECONDS} seconds..."
    )

    time.sleep(RECONNECT_SECONDS)