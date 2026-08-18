import time
import requests
from Core.page_engine import get_page

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

TABLE = "commands"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}
def clear_user_memory(session_id, channel):

    response = requests.patch(

        f"{SUPABASE_URL}/rest/v1/user_memory",

        headers={
            **HEADERS,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },

        params={
            "session_id": f"eq.{session_id}",
            "channel": f"eq.{channel}"
        },

        json={
            "memory_json": {}
        },

        timeout=10
    )

    if response.status_code in (200, 204):

        print(
            "MEMORY CLEARED:",
            session_id
        )

        return True

    print(
        "MEMORY CLEAR ERROR:",
        response.status_code,
        response.text
    )

    return False
def check_commands(

    bot_config,

    show_page,

    show_popup,

    show_command

):

    print("Command Watcher started")

    while True:

        try:

            response = requests.get(

                f"{SUPABASE_URL}/rest/v1/{TABLE}",

                headers=HEADERS,

                params={

                    "select": "*",

                    "target_bot": f"eq.{bot_config['bot']}",

                    "status": "eq.new",

                    "order": "id.asc"

                },

                timeout=10

            )

            if response.status_code != 200:

                time.sleep(1)

                continue

            rows = response.json()

            for row in rows:

                command = row["command"]

                print("COMMAND:", command)

                chat_id = row["session_id"]

                data = get_page(command)

                if not data:
                    continue

                memory_response = requests.get(

                    f"{SUPABASE_URL}/rest/v1/user_memory",

                    headers=HEADERS,

                    params={
                        "select": "memory_json",
                        "session_id": f"eq.{chat_id}",
                        "channel": f"eq.{row['channel']}",
                        "limit": 1
                    },

                    timeout=10

                )

                if memory_response.status_code != 200:
                    continue

                rows = memory_response.json()

                if not rows:
                    continue

                memory = rows[0]["memory_json"]
                print("🧠 COMMAND MEMORY:", memory)

                data["messages"] = []

                for key, value in memory.items():

                    data["messages"].append(
                        f"{key}: {value}"
                    )

                print(memory)
                
                engine = data.get("engine", "page")

                if engine == "popup":

                    show_popup(
                        chat_id,
                        data
                    )

                elif engine == "command":

                    show_command(
                        chat_id,
                        data
                    )

                else:

                    show_page(
                        chat_id,
                        data
                    )
                    print("PAGE SHOWN")
 
                patch_response = requests.patch(

                    f"{SUPABASE_URL}/rest/v1/{TABLE}?id=eq.{row['id']}",

                    headers={
                        **HEADERS,
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },

                    json={
                        "status": "done"
                    },

                    timeout=10

                )

                print(
                    "PATCH:",
                    patch_response.status_code,
                    patch_response.text
                )

# ========================================
# COMMAND DONE → CLEAR MEMORY
# ========================================

                if patch_response.status_code in (200, 204):

                    clear_user_memory(
                        chat_id,
                        row["channel"]
       )

                else:

                    print(
                        "MEMORY NOT CLEARED — COMMAND NOT DONE"
                    )

        except Exception as e:

            print(e)

        time.sleep(1)