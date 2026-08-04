import time
import requests

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
def check_commands(

    bot,

    bot_config,

    show_page,

    show_popup

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

        except Exception as e:

            print(e)

        time.sleep(1)