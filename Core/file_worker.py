import time
import requests
import cloudinary
import cloudinary.uploader


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

CONFIG_URL = BASE + "Core/config.json"


TABLE = "file_events"
ASSETS_TABLE = "assets"


config = requests.get(
    CONFIG_URL,
    timeout=10
).json()


SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]


HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


cloudinary.config(
    cloud_name=config["cloudinary_cloud"],
    api_key=config["cloudinary_api_key"],
    api_secret=config["cloudinary_api_secret"]
)


last_id = 0
ASSETS_TABLE = "assets"
DELIVERY_TABLE = "file_delivery"

def get_events():

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/{TABLE}",

        headers=HEADERS,

        params={
            "select": "*",
            "id": f"gt.{last_id}",
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


def update_event(event_id, data):

    response = requests.patch(

        f"{SUPABASE_URL}/rest/v1/{TABLE}",

        headers=HEADERS,

        params={
            "id": f"eq.{event_id}"
        },

        json=data,

        timeout=10
    )

    return response.status_code in (200, 204)


def create_asset(event, result):

    response = requests.post(

        f"{SUPABASE_URL}/rest/v1/{ASSETS_TABLE}",

        headers={
            **HEADERS,
            "Prefer": "return=representation"
        },

        json={
            "asset_id": "TEMP",
            "session_id": event["session_id"],
            "source_bot": event.get("source_bot"),
            "channel": event.get("channel"),
            "file_name": event.get("file_name"),
            "file_type": event.get("file_type"),
            "cloudinary_public_id": result["public_id"],
            "cloudinary_url": result["secure_url"],
            "status": "ready"
        },

        timeout=10
    )

    if response.status_code not in (200, 201):

        raise Exception(
            "Asset create error: "
            + response.text
        )

    row = response.json()[0]

    asset_id = f"AST_{row['id']:06d}"

    update_response = requests.patch(

        f"{SUPABASE_URL}/rest/v1/{ASSETS_TABLE}",

        headers=HEADERS,

        params={
            "id": f"eq.{row['id']}"
        },

        json={
            "asset_id": asset_id
        },

        timeout=10
    )

    if update_response.status_code not in (200, 204):

        raise Exception(
            "Asset ID update error: "
            + update_response.text
        )

    return asset_id
def create_delivery(event, asset_id):

    source_bot = event.get("source_bot")
    channel = event.get("channel")

    pairs = {
        "telegram_bot1": "telegram_bot2",
        "telegram_bot2": "telegram_bot1",
        "whatsapp_bot1": "whatsapp_bot2",
        "whatsapp_bot2": "whatsapp_bot1"
    }

    target_bot = pairs.get(source_bot)

    if not target_bot:
        raise Exception(
            f"Unknown source bot: {source_bot}"
        )

    response = requests.post(

        f"{SUPABASE_URL}/rest/v1/{DELIVERY_TABLE}",

        headers={
            **HEADERS,
            "Prefer": "return=minimal"
        },

        json={
            "chat_id": event.get("chat_id"),
            "asset_id": asset_id,
            "session_id": event["session_id"],
            "source_bot": source_bot,
            "target_bot": target_bot,
            "channel": channel,
            "status": "queued"
        },

        timeout=10
    )

    if response.status_code not in (200, 201):

        raise Exception(
            "Delivery create error: "
            + response.text
        )

    print()
    print("📤 FILE DELIVERY")
    print("ASSET:", asset_id)
    print("SESSION:", event["session_id"])
    print("SOURCE:", source_bot)
    print("TARGET:", target_bot)
    print("🟢 FILE QUEUED FOR PARTNER")

def process_event(event):

    print()
    print("📥 FILE RECEIVED")

    print(
        "SESSION:",
        event["session_id"]
    )

    print(
        "FILE:",
        event.get("file_name")
    )

    update_event(
        event["id"],
        {
            "status": "processing"
        }
    )

    file_url = event.get("file_url")

    if not file_url:

        raise Exception(
            "file_url is missing"
        )

    print("☁️ Uploading to Cloudinary...")

    resource_type = (
        "raw"
        if event.get("file_type") == "document"
        else "image"
    )
    print("FILE SOURCE:", event.get("file_source"))
    print("GALLERY PUBLIC ID:", event.get("cloudinary_public_id"))

    if event.get("file_source") == "gallery":

        result = {
            "public_id": event["cloudinary_public_id"],
            "secure_url": event["file_url"]
        }

    else:

        resource_type = (
            "raw"
            if event.get("file_type") == "document"
            else "image"
        )

        result = cloudinary.uploader.upload(
            file_url,
            folder=f"incoming/{event['session_id']}",
            resource_type=resource_type
        )

    print(
        "Cloudinary:",
        result["public_id"]
    )

    asset_id = create_asset(
        event,
        result
    )

    update_event(
        event["id"],
        {
            "status": "ready",
            "asset_id": asset_id
        }
    )

    print()
    print("✅ FILE READY")
    print("AST_ID:", asset_id)
    print("SESSION_ID:", event["session_id"])
    print("URL:", result["secure_url"])
    create_delivery(
        event,
        asset_id
    )
    print()


print("🟢 File Worker Running...")
print("Waiting for files...")


while True:

    try:

        events = get_events()

        for event in events:

            last_id = event["id"]

            try:

                process_event(event)

            except Exception as e:

                print(
                    "🔴 FILE ERROR:",
                    e
                )

                update_event(
                    event["id"],
                    {
                        "status": "error"
                    }
                )

    except Exception as e:

        print(
            "🔴 WORKER ERROR:",
            e
        )

    time.sleep(1)