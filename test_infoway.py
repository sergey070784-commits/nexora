import os
import json
import time
import uuid
import websocket

API_KEY = os.getenv("INFOWAY_API_KEY")

if not API_KEY:
    print("ERROR: INFOWAY_API_KEY is not set")
    raise SystemExit(1)

URL = f"wss://data.infoway.io/ws?business=common&apikey={API_KEY}"


def on_open(ws):
    print("CONNECTED")

    request = {
        "code": 10000,
        "trace": str(uuid.uuid4()),
        "data": {
            "codes": "USOIL"
        }
    }

    ws.send(json.dumps(request))
    print("SUBSCRIBED: USOIL")


def on_message(ws, message):
    try:
        data = json.loads(message)
        print(
            time.strftime("%H:%M:%S"),
            json.dumps(data, ensure_ascii=False)
        )
    except Exception:
        print("RAW:", message)


def on_error(ws, error):
    print("ERROR:", error)


def on_close(ws, close_status_code, close_msg):
    print("CLOSED:", close_status_code, close_msg)


ws = websocket.WebSocketApp(
    URL,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)

print("Starting Infoway USOIL WebSocket...")
ws.run_forever()