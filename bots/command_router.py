import time
import requests
import json

NOTIFY_ROUTES_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "navigation/notify_routes.json"
)

CONFIG_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Core/config.json"
)

import sys

CONFIG_NAME = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "bot1_config.json"
)

BOT_CONFIG_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    f"Core/{CONFIG_NAME}"
)

config = requests.get(
    CONFIG_URL,
    timeout=10
).json()

bot_config = requests.get(
    BOT_CONFIG_URL,
    timeout=10
).json()
print(
    f"Router: {bot_config['bot']} -> {bot_config['pair']}"
)
SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

TABLE = "events"
MEMORY_TABLE = "user_memory"
COMMANDS_TABLE = "commands"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

notify_routes = {}

last_routes_update = 0

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
        },
        timeout=10
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

    if now - last_routes_update < 1800:
        return

    try:

        response = requests.get(
            NOTIFY_ROUTES_URL,
            timeout=10
        )

        if response.status_code == 200:

            notify_routes = response.json()

            last_routes_update = now

            print(
                f"Loaded {len(notify_routes)} notify routes"
            )

    except Exception as e:

        print("Notify routes error:", e)


init_last_id()

def save_command(
    source_bot,
    target_bot,
    channel,
    session_id,
    command
):

    # ========================================
    # CHECK: COMMAND ALREADY EXISTS
    # ========================================

    check_response = requests.get(

        f"{SUPABASE_URL}/rest/v1/{COMMANDS_TABLE}",

        headers=HEADERS,

        params={
            "select": "id,status",
            "session_id": f"eq.{session_id}",
            "command": f"eq.{command}",
            "status": "eq.new",
            "limit": 1
        },

        timeout=10

    )

    if check_response.status_code != 200:

        print(
            "Command check error:",
            check_response.status_code,
            check_response.text
        )

        return

    existing = check_response.json()

    if existing:

        print(
            "COMMAND ALREADY SENT:",
            command,
            "SESSION:",
            session_id,
            "STATUS:",
            existing[0]["status"]
        )

        return

    # ========================================
    # CREATE NEW COMMAND
    # ========================================

    data = {

        "source_bot": source_bot,

        "target_bot": target_bot,

        "channel": channel,

        "session_id": session_id,

        "command": command,

        "status": "new"

    }

    response = requests.post(

        f"{SUPABASE_URL}/rest/v1/{COMMANDS_TABLE}",

        headers={
            **HEADERS,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },

        json=data,

        timeout=10

    )

    if response.status_code in (200, 201):

        print(
            "Command created:",
            command
        )

    else:

        print(
            "Command error:",
            response.status_code,
            response.text
        )

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

        if response.status_code != 200:

            print(
                "Supabase error:",
                response.status_code
            )

            time.sleep(1)

            continue

        rows = response.json()

        for row in rows:

            last_id = row["id"]

            button = row.get("value")

            print(
                "EVENT:",
                row.get("bot"),
                "ROUTER:",
                bot_config["bot"],
                "BTN:",
                button
            )

            if row.get("bot") != bot_config["bot"]:
                continue
            print(
                "🔎 ROUTE CHECK:",
                repr(button),
                "MATCH:",
                button in notify_routes
            )

            if button not in notify_routes:
                continue
            
            command = notify_routes[button]

            print("FOUND:", command)

            save_command(

                source_bot=row["bot"],

                target_bot=bot_config["pair"],

                channel=row["channel"],

                session_id=row["session_id"],

                command=notify_routes[button]

            )

    except Exception as e:

        print("ERROR:", e)

    time.sleep(1)