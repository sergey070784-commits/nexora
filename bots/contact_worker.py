import time
import requests


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)


CONFIG_URL = BASE + "Core/config.json"

ROUTES_URL = (
    BASE +
    "Service/contact_routes.json"
)


EVENTS_TABLE = "events"


# ========================================
# CONFIG
# ========================================

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


# ========================================
# CONTACT ROUTES
# ========================================

routes_response = requests.get(
    ROUTES_URL,
    timeout=10
)

routes_response.raise_for_status()

CONTACT_ROUTES = routes_response.json()


print()
print("📋 CONTACT ROUTES LOADED")
print(
    "CTN:",
    list(CONTACT_ROUTES.keys())
)


# ========================================
# ACTIVE CONTACTS
# ========================================

active_contacts = {}


# ========================================
# EVENT POSITION
# ========================================

response = requests.get(

    f"{SUPABASE_URL}/rest/v1/{EVENTS_TABLE}",

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
    else:
        last_id = 0

else:

    print(
        "🔴 EVENTS INIT ERROR:",
        response.status_code,
        response.text
    )

    last_id = 0


# ========================================
# GET EVENTS
# ========================================

def get_events():

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/{EVENTS_TABLE}",

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
            "🔴 EVENTS ERROR:",
            response.status_code,
            response.text
        )

        return []

    return response.json()


# ========================================
# PROCESS EVENT
# ========================================

def process_event(event):

    session_id = event.get(
        "session_id"
    )

    value = event.get(
        "value"
    )

    message = event.get(
        "message"
    )


    # ====================================
    # CTN BUTTON
    # ====================================

    if value and value.startswith("CTN_"):

        ctn_id = value

        print()
        print("📋 CONTACT ENTRY")
        print("SESSION:", session_id)
        print("CTN:", ctn_id)


        page_name = CONTACT_ROUTES.get(
            ctn_id
        )


        if not page_name:

            print(
                "🔴 CTN NOT FOUND IN CONTACT ROUTES:",
                ctn_id
            )

            return


        active_contacts[
            str(session_id)
        ] = {

            "ctn": ctn_id,
            "page": page_name
        }


        print(
            "🟢 CONTACT ACTIVE"
        )

        print(
            "SESSION:",
            session_id
        )

        print(
            "CTN:",
            ctn_id
        )

        print(
            "PAGE:",
            page_name
        )

        return


    # ====================================
    # USER TEXT
    # ====================================

    if message:

        session_key = str(
            session_id
        )

        contact = active_contacts.get(
            session_key
        )


        if not contact:

            return


        print()
        print("📥 CONTACT TEXT")
        print(
            "SESSION:",
            session_id
        )
        print(
            "CTN:",
            contact["ctn"]
        )
        print(
            "PAGE:",
            contact["page"]
        )
        print(
            "TEXT:",
            message
        )

        print(
            "✅ CONTACT TEXT RECEIVED"
        )
        # ========================================
# WORKER
# ========================================

print()
print("🟢 Contact Worker Running...")
print("Waiting for Contact...")


while True:

    try:

        rows = get_events()

        for event in rows:

            last_id = event["id"]

            try:

                process_event(
                    event
                )

            except Exception as e:

                print(
                    "🔴 CONTACT EVENT ERROR:",
                    e
                )

    except Exception as e:

        print(
            "🔴 CONTACT WORKER ERROR:",
            e
        )

    time.sleep(1)