import time
import requests

# ==========================
# НАСТРОЙКИ
# ==========================
NOTIFY_URL = "https://raw.githubusercontent.com/sergey070784-commits/nexora/main/navigation/notify_routes.json"

BOT_CONFIG_URL = "https://raw.githubusercontent.com/sergey070784-commits/nexora/main/Core/bot_config.json"

CONFIG_URL = "https://raw.githubusercontent.com/sergey070784-commits/nexora/main/Core/config.json"

bot_config = requests.get(
    BOT_CONFIG_URL,
    timeout=10
).json()

config = requests.get(
    CONFIG_URL,
    timeout=10
).json()

notify_routes = {}
last_routes_update = 0

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

TABLE = "events"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}


last_id = 0
def init_last_id():

    global last_id

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
        headers=HEADERS,
        params={
            "select": "id",
            "order": "id.desc",
            "limit": 1
        }
    )

    if response.status_code == 200:

        rows = response.json()

        if rows:
            last_id = rows[0]["id"]

    print(f"Start from ID {last_id}")
def load_notify_routes():

    global notify_routes
    global last_routes_update

    now = time.time()

    if now - last_routes_update < 300:
        return

    try:

        response = requests.get(
            NOTIFY_URL,
            timeout=10
        )

        if response.status_code == 200:

            notify_routes = response.json()
            last_routes_update = now

            print(
                f"Loaded {len(notify_routes)} notify routes"
            )

    except Exception as e:

        print(
            "Notify routes error:",
            e
        )
print("Journal Watcher started...\n")
init_last_id()
def send_command(command):

    response = requests.post(

        "http://127.0.0.1:5001/command",

        json=command,

        timeout=10

    )

    print(response.text)
while True:

    load_notify_routes()

    try:

        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{TABLE}",
            headers=HEADERS,
            params={
                "select": "*",
                "id": f"gt.{last_id}",
                "order": "id.asc"
            },
            timeout=10
        )

        if response.status_code == 200:

            rows = response.json()

            for row in rows:

                last_id = row["id"]

                if row.get("event") != "button_click":
                    continue

                button = row.get("value")

                if button not in notify_routes:
                    continue

                # Только Telegram и WhatsApp создают команды
                if row.get("channel") not in (
                    "telegram",
                    "whatsapp"
                ):
                    continue

                command = {
                    "source_bot": row.get("bot"),
                    "target_bot": bot_config["pair"],
                    "channel": row.get("channel"),
                    "session_id": row.get("session_id"),
                    "page": notify_routes[button]
                }

                response = requests.post(

                    f"{SUPABASE_URL}/rest/v1/commands",

                    headers={
                        **HEADERS,
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },

                    json=command,

                    timeout=10

                )

                if response.status_code in (200, 201):

                    print("Command queued")

                else:

                    print("Command error")
                    print(response.text)

        else:

            print("Supabase error:", response.status_code)
            print(response.text)

    except Exception as e:

        print("ERROR:", e)

    time.sleep(1)
