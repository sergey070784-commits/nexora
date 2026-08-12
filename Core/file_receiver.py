import sys
import time
import requests


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

CONFIG_URL = BASE + "Core/config.json"


CONFIG_NAME = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "bot1_config.json"
)

BOT_CONFIG_URL = (
    BASE
    + "Core/"
    + CONFIG_NAME
)


config = requests.get(
    CONFIG_URL,
    timeout=10
).json()


bot_config = requests.get(
    BOT_CONFIG_URL,
    timeout=10
).json()


MY_BOT = bot_config["bot"]
PAIR_BOT = bot_config["pair"]


print(
    f"File Receiver: {MY_BOT}"
)

print(
    f"Partner: {PAIR_BOT}"
)


SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]


HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


TABLE = "file_messages"


last_id = 0


def get_messages():

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/{TABLE}",

        headers=HEADERS,

        params={
            "select": "*",
            "id": f"gt.{last_id}",
            "target_bot": f"eq.{MY_BOT}",
            "status": "eq.new",
            "order": "id.asc"
        },

        timeout=10
    )

    if response.status_code != 200:

        print(
            "Supabase error:",
            response.status_code,
            response.text
        )

        return []

    return response.json()


def update_message(
    message_id,
    status
):

    response = requests.patch(

        f"{SUPABASE_URL}/rest/v1/{TABLE}",

        headers=HEADERS,

        params={
            "id": f"eq.{message_id}"
        },

        json={
            "status": status
        },

        timeout=10
    )

    return response.status_code in (200, 204)


def get_asset(asset_id):

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/assets",

        headers=HEADERS,

        params={
            "select": "*",
            "asset_id": f"eq.{asset_id}",
            "limit": 1
        },

        timeout=10
    )

    if response.status_code != 200:

        print(
            "Asset error:",
            response.status_code,
            response.text
        )

        return None

    rows = response.json()

    if not rows:
        return None

    return rows[0]


def process_message(message):

    print()
    print("📥 FILE MESSAGE")

    print(
        "SOURCE:",
        message["source_bot"]
    )

    print(
        "TARGET:",
        message["target_bot"]
    )

    print(
        "ASSET:",
        message["asset_id"]
    )

    print(
        "SESSION:",
        message["session_id"]
    )


    update_message(
        message["id"],
        "processing"
    )


    asset = get_asset(
        message["asset_id"]
    )


    if not asset:

        print(
            "🔴 ASSET NOT FOUND"
        )

        update_message(
            message["id"],
            "error"
        )

        return


    print()
    print("✅ ASSET FOUND")

    print(
        "FILE:",
        asset["file_name"]
    )

    print(
        "TYPE:",
        asset["file_type"]
    )

    print(
        "URL:",
        asset["cloudinary_url"]
    )


    # ------------------------------------------------
    # Пока только получение файла.
    # Отправку в Telegram / WhatsApp подключим следующим этапом.
    # ------------------------------------------------

    update_message(
        message["id"],
        "received"
    )


    print()
    print("🟢 FILE RECEIVED BY PARTNER")


print()
print(
    "🟢 File Receiver Running..."
)

print(
    "Waiting for files..."
)


while True:

    try:

        rows = get_messages()

        for row in rows:

            last_id = row["id"]

            try:

                process_message(row)

            except Exception as e:

                print(
                    "🔴 RECEIVER ERROR:",
                    e
                )

                update_message(
                    row["id"],
                    "error"
                )

    except Exception as e:

        print(
            "🔴 WORKER ERROR:",
            e
        )

    time.sleep(1)