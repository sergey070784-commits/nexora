import time
import requests
import json

# ==========================
# НАСТРОЙКИ
# ==========================

BTN_DICTIONARY_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "pages/pickers/dictionary/btn_dictionary.json"
)

CONFIG_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Core/config.json"
)

config = requests.get(
    CONFIG_URL,
    timeout=10
).json()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

TABLE = "events"
MEMORY_TABLE = "user_memory"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

btn_dictionary = {}

last_dictionary_update = 0

last_id = 0
last_memory = {}
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


def load_btn_dictionary():

    global btn_dictionary
    global last_dictionary_update

    now = time.time()

    if now - last_dictionary_update < 1800:
        return

    try:

        response = requests.get(
            BTN_DICTIONARY_URL,
            timeout=10
        )

        if response.status_code == 200:

            btn_dictionary = response.json()

            last_dictionary_update = now

            print(
                f"Loaded {len(btn_dictionary)} BTN records"
            )

    except Exception as e:

        print("Dictionary error:", e)


init_last_id()

def save_memory(session_id, channel, memory):

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/{MEMORY_TABLE}",

        headers=HEADERS,

        params={
            "select": "memory_json",
            "session_id": f"eq.{chat_id}",
            "limit": 1
        },

        timeout=10

    )

    if response.status_code != 200:
        print("Memory lookup failed")
        return

    rows = response.json()

    if rows:

        memory_id = rows[0]["id"]

        current_memory = rows[0].get("memory_json") or {}

        current_memory.update(memory)

        response = requests.patch(

            f"{SUPABASE_URL}/rest/v1/{MEMORY_TABLE}?id=eq.{memory_id}",

            headers={
                **HEADERS,
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },

            json={
                "memory_json": current_memory
            },

            timeout=10

        )

        if response.status_code in (200, 204):
            print("Memory updated")
        else:
            print("Update failed:", response.text)

    else:

        response = requests.post(

            f"{SUPABASE_URL}/rest/v1/{MEMORY_TABLE}",

            headers={
                **HEADERS,
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },

            json={
                "session_id": session_id,
                "channel": channel,
                "memory_json": memory
            },

            timeout=10

        )

        if response.status_code in (200, 201):
            print("Memory created")
        else:
            print("Insert failed:", response.text)

while True:

    load_btn_dictionary()

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

            print(response.text)

            time.sleep(1)

            continue

        rows = response.json()

        for row in rows:

            last_id = row["id"]

            button = row.get("value")

            if button and "=" in button:

                field, value = button.split("=", 1)

                save_memory(

                    row["session_id"],

                    row["channel"],

                    {
                        field.lower(): value
                    }

                )

                continue

            if button not in btn_dictionary:
                continue

            item = btn_dictionary[button]

            memory = {
                item["field"]: item["value"]
            }

            print(
                json.dumps(
                    memory,
                    indent=4,
                    ensure_ascii=False
                )
            )

            save_memory(
                row["session_id"],
                row["channel"],
                memory
            )

    except Exception as e:

        print(
            "ERROR:",
            e
        )

    time.sleep(1)