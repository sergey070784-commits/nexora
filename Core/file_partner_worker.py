import sys
import time
import requests


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

CONFIG_URL = BASE + "Core/config.json"


# -------------------------------------------------
# BOT CONFIG
# -------------------------------------------------

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
PARTNER_BOT = bot_config["pair"]
CHANNEL = bot_config["channel"]


print(
    f"File Partner: {MY_BOT} -> {PARTNER_BOT}"
)


# -------------------------------------------------
# SUPABASE
# -------------------------------------------------

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]


HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


FILE_DELIVERY_TABLE = "file_delivery"
FILE_MESSAGES_TABLE = "file_messages"


last_id = 0


# -------------------------------------------------
# GET FILE DELIVERY
# -------------------------------------------------

def get_file_deliveries():

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/"
        f"{FILE_DELIVERY_TABLE}",

        headers=HEADERS,

        params={
            "select": "*",
            "id": f"gt.{last_id}",
            "source_bot": f"eq.{MY_BOT}",
            "status": "eq.queued",
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


# -------------------------------------------------
# UPDATE DELIVERY
# -------------------------------------------------

def update_delivery(
    delivery_id,
    status
):

    response = requests.patch(

        f"{SUPABASE_URL}/rest/v1/"
        f"{FILE_DELIVERY_TABLE}",

        headers=HEADERS,

        params={
            "id": f"eq.{delivery_id}"
        },

        json={
            "status": status
        },

        timeout=10
    )

    return response.status_code in (200, 204)


# -------------------------------------------------
# GET ASSET
# -------------------------------------------------

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
            "Asset lookup error:",
            response.status_code,
            response.text
        )

        return None

    rows = response.json()

    if not rows:
        return None

    return rows[0]


# -------------------------------------------------
# CREATE FILE MESSAGE
# -------------------------------------------------

def create_file_message(
    item,
    asset
):

    data = {
        "chat_id": item.get("chat_id"),

        "asset_id": asset["asset_id"],

        "session_id": asset["session_id"],

        "source_bot": MY_BOT,

        "target_bot": PARTNER_BOT,

        "source_channel": CHANNEL,

        "target_channel": CHANNEL,

        "status": "new"

    }

    response = requests.post(

        f"{SUPABASE_URL}/rest/v1/"
        f"{FILE_MESSAGES_TABLE}",

        headers={
            **HEADERS,
            "Prefer": "return=minimal"
        },

        json=data,

        timeout=10
    )

    if response.status_code not in (200, 201):

        print(
            "File message error:",
            response.status_code,
            response.text
        )

        return False

    print(
        "📨 FILE MESSAGE CREATED"
    )

    print(
        "SOURCE:",
        MY_BOT
    )

    print(
        "TARGET:",
        PARTNER_BOT
    )

    print(
        "ASSET:",
        asset["asset_id"]
    )

    return True


# -------------------------------------------------
# PROCESS DELIVERY
# -------------------------------------------------

def process_delivery(item):

    print()
    print("📤 FILE DELIVERY")

    print(
        "ASSET:",
        item["asset_id"]
    )

    print(
        "SESSION:",
        item["session_id"]
    )

    print(
        "SOURCE:",
        MY_BOT
    )

    print(
        "TARGET:",
        PARTNER_BOT
    )

    update_delivery(
        item["id"],
        "processing"
    )

    asset = get_asset(
        item["asset_id"]
    )

    if not asset:

        print(
            "🔴 ASSET NOT FOUND:",
            item["asset_id"]
        )

        update_delivery(
            item["id"],
            "error"
        )

        return

    print()
    print("✅ ASSET FOUND")

    print(
        "AST_ID:",
        asset["asset_id"]
    )

    print(
        "FILE:",
        asset["file_name"]
    )

    print(
        "TYPE:",
        asset["file_type"]
    )

    print(
        "SESSION:",
        asset["session_id"]
    )

    print(
        "URL:",
        asset["cloudinary_url"]
    )

    created = create_file_message(
        item,
        asset
    )

    if not created:

        update_delivery(
            item["id"],
            "error"
        )

        return

    update_delivery(
        item["id"],
        "done"
    )

    print(
        "🟢 FILE QUEUED FOR PARTNER"
    )


# -------------------------------------------------
# START
# -------------------------------------------------

print(
    "🟢 File Partner Worker Running..."
)

print(
    "Waiting for FILE_READY..."
)


# -------------------------------------------------
# LOOP
# -------------------------------------------------

while True:

    try:

        rows = get_file_deliveries()

        for row in rows:

            last_id = row["id"]

            try:

                process_delivery(row)

            except Exception as e:

                print(
                    "🔴 DELIVERY ERROR:",
                    e
                )

                update_delivery(
                    row["id"],
                    "error"
                )

    except Exception as e:

        print(
            "🔴 WORKER ERROR:",
            e
        )

    time.sleep(1)