import time
import requests

from Core.event_logger import send_event


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
print("📋 WA CONTACT ROUTES LOADED")
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
        "🔴 WA CONTACT EVENTS INIT ERROR:",
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
            "bot": "eq.whatsapp_bot1",
            "order": "id.asc"
        },

        timeout=10
    )

    if response.status_code != 200:

        print(
            "🔴 WA CONTACT EVENTS ERROR:",
            response.status_code,
            response.text
        )

        return []

    return response.json()


# ========================================
# WAIT FOR MEMORY
# ========================================

def wait_for_memory_value(
    session_id,
    channel,
    field,
    value,
    timeout=10
):

    start_time = time.time()

    while time.time() - start_time < timeout:

        response = requests.get(

            f"{SUPABASE_URL}/rest/v1/user_memory",

            headers=HEADERS,

            params={
                "select": "memory_json",
                "session_id": f"eq.{session_id}",
                "channel": f"eq.{channel}",
                "limit": 1
            },

            timeout=10
        )

        if response.status_code == 200:

            rows = response.json()

            if rows:

                memory = rows[0].get(
                    "memory_json"
                ) or {}

                if str(
                    memory.get(field)
                ) == str(value):

                    print(
                        "🧠 MEMORY CONFIRMED:",
                        field,
                        "=",
                        value
                    )

                    return True

        time.sleep(0.2)

    print(
        "🔴 MEMORY NOT CONFIRMED:",
        field,
        "=",
        value
    )

    return False


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

    message = event.get("message")

    channel = event.get(
        "channel"
    )

    bot = event.get(
        "bot"
    )


    # ====================================
    # CONTACT BUTTON
    # ====================================

    if value and value.startswith("CTN_"):

        ctn_id = value

        print()
        print("📋 WA CONTACT ENTRY")
        print("SESSION:", session_id)
        print("CTN:", ctn_id)

        page_name = CONTACT_ROUTES.get(
            ctn_id
        )

        if not page_name:

            print(
                "🔴 WA CTN NOT FOUND:",
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
            "🟢 WA CONTACT ACTIVE"
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
    # CONTACT TEXT
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
        print("📥 WA CONTACT TEXT")

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


        # =================================
        # LOAD CURRENT CONTACT PAGE
        # =================================

        page_name = contact["page"]

        page_url = (
            BASE +
            "Service/contact_viewer/" +
            page_name +
            ".json"
        )

        response = requests.get(
            page_url,
            timeout=10
        )

        response.raise_for_status()

        page_data = response.json()

        field = page_data.get(
            "field"
        )

        next_id = page_data.get(
            "next"
        )

        print(
            "FIELD:",
            field
        )

        print(
            "NEXT:",
            next_id
        )


        # =================================
        # SAVE VALUE → MEMORY PIPELINE
        # =================================

        contact_bot_config = {

            "channel": channel,

            "bot": bot

        }

        send_event(

            contact_bot_config,

            session_id,

            value=f"{field}={message}"

        )

        print(
            "💾 WA CONTACT VALUE SENT:",
            f"{field}={message}"
        )


        # =================================
        # NEXT CONTACT PAGE
        # =================================

        if next_id and next_id.startswith(
            "CTN_"
        ):

            next_page = CONTACT_ROUTES.get(
                next_id
            )

            if not next_page:

                print(
                    "🔴 WA NEXT CONTACT ROUTE NOT FOUND:",
                    next_id
                )

                return

            contact["ctn"] = next_id

            contact["page"] = next_page


            send_event(

                contact_bot_config,

                session_id,

                value=f"CONTACT_NEXT:{next_id}"

            )

            print(
                "➡️ WA CONTACT NAVIGATION SENT:",
                next_id
            )

            print(
                "➡️ WA NEXT CONTACT PAGE:",
                next_page
            )

            return

        print(
            "🔎 WA CONTACT DECISION:",
            "CURRENT CTN =",
            contact["ctn"],
            "| NEXT =",
            next_id,
            "| FIELD =",
            field
      )


        # =================================
        # CONTACT FINISHED
        # =================================

        if next_id and next_id.startswith(
            "BTN_"
        ):

            print()
            print(
                "✅ WA CONTACT COMPLETE"
            )

            print(
                "SESSION:",
                session_id
            )

            print(
                "CONTACT DATA:",
                contact
            )

            print(
                "➡️ RETURN BTN:",
                next_id
            )


            memory_confirmed = wait_for_memory_value(

                session_id,

                channel,

                field.lower(),

                message

            )


            if not memory_confirmed:

                print(
                    "🔴 WA CONTACT STOPPED — MEMORY NOT READY"
                )

                return


            # =================================
            # NORMAL BTN
            # =================================

            send_event(

                contact_bot_config,

                session_id,

                value=next_id

            )


            # =================================
            # CONTACT NAVIGATION
            # =================================

            send_event(

                contact_bot_config,

                session_id,

                value=f"CONTACT_NEXT:{next_id}"

            )


            print(
                "➡️ WA CONTACT NAVIGATION SENT:",
                next_id
            )

            print(
                "📤 WA CONTACT BTN SENT:",
                next_id
            )


            active_contacts.pop(
                session_key,
                None
            )

            return


# ========================================
# WORKER
# ========================================

print()
print("🟢 WA Contact Worker Running...")
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
                    "🔴 WA CONTACT EVENT ERROR:",
                    e
                )

    except Exception as e:

        print(
            "🔴 WA CONTACT WORKER ERROR:",
            e
        )

    time.sleep(1)