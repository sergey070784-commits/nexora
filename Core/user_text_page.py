import time
import requests
from datetime import datetime


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


TABLE = "user_text_page"


HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}


def check_user_text_page(
    bot_config,
    show_page
):

    print(
        "USER TEXT PAGE WORKER STARTED:",
        bot_config["bot"]
    )

    while True:

        try:

            response = requests.get(

                f"{SUPABASE_URL}/rest/v1/"
                f"{TABLE}",

                headers=HEADERS,

                params={

                    "select": "*",

                    "target_bot":
                        f"eq.{bot_config['bot']}",

                    "status":
                        "eq.new",

                    "order":
                        "id.asc"

                },

                timeout=10
            )

            if response.status_code != 200:

                print(
                    "USER TEXT PAGE GET ERROR:",
                    response.status_code,
                    response.text[:300]
                )

                time.sleep(1)

                continue

            rows = response.json()

            for row in rows:

                print()
                print(
                    "📄 USER TEXT PAGE FOR BOT"
                )

                print(
                    "SOURCE:",
                    row.get("source_bot")
                )

                print(
                    "TARGET:",
                    row.get("target_bot")
                )

                print(
                    "CHANNEL:",
                    row.get("channel")
                )

                print(
                    "SESSION:",
                    row.get("session_id")
                )

                chat_id = row.get(
                    "session_id"
                )

                if row.get("channel") == "telegram":

                    chat_id = int(chat_id)

                page = row.get("page")

                if not page:

                    print(
                        "⚠️ PAGE EMPTY:",
                        row["id"]
                    )

                    continue

                print(
                    "🚀 SHOW USER TEXT PAGE"
                )

                show_page(
                    chat_id,
                    page
                )

                patch_response = requests.patch(

                    f"{SUPABASE_URL}/rest/v1/"
                    f"{TABLE}",

                    headers={
                        **HEADERS,
                        "Content-Type":
                            "application/json",
                        "Prefer":
                            "return=minimal"
                    },

                    params={
                        "id":
                            f"eq.{row['id']}"
                    },

                    json={
                        "status": "sent"
                    },

                    timeout=10
                )

                print(
                    "PAGE PATCH:",
                    patch_response.status_code
                )

        except Exception as e:

            print(
                "🔴 USER TEXT PAGE WORKER ERROR:",
                e
            )

        time.sleep(1)