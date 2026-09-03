import requests
import time
import json


# ========================================
# SUPABASE
# ========================================

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

config = requests.get(
    BASE + "Core/config.json",
    timeout=10
).json()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}


# ========================================
# IGNORE JSON
# ========================================

IGNORE_URL = (
    BASE +
    "pages/pickers/user_text_ignore.json"
)


def get_ignore_types():

    response = requests.get(
        IGNORE_URL,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return [
        item["type"]
        for item in data.get("ignore", [])
        if item.get("type")
    ]


# ========================================
# QUEUE
# ========================================

def get_pending_messages():

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_queue"
    )

    params = {
        "select": (
            "id,message_id,session_id,"
            "message_text,last_btn,status"
        ),
        "status": "eq.pending",
        "order": "id.asc",
        "limit": "20"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ========================================
# EVENTS
# ========================================

def get_ctn_event(
    session_id,
    message_id
):

    # Get the original message time
    message_url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_messages"
    )

    message_params = {
        "select": "created_at",
        "id": f"eq.{message_id}",
        "limit": "1"
    }

    response = requests.get(
        message_url,
        headers=HEADERS,
        params=message_params,
        timeout=10
    )

    response.raise_for_status()

    message_data = response.json()

    if not message_data:
        return None

    message_created_at = (
        message_data[0]["created_at"]
    )

    # Find the latest CTN before the message
    events_url = (
        f"{SUPABASE_URL}/rest/v1/events"
    )

    events_params = {
        "select": "id,value,created_at",
        "session_id": f"eq.{session_id}",
        "value": "like.CTN_*",
        "created_at": f"lte.{message_created_at}",
        "order": "created_at.desc",
        "limit": "1"
    }

    response = requests.get(
        events_url,
        headers=HEADERS,
        params=events_params,
        timeout=10
    )

    response.raise_for_status()

    events = response.json()

    if not events:
        return None

    return events[0]


# ========================================
# READY TABLE
# ========================================

def ready_exists(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_ready"
    )

    params = {
        "select": "id",
        "message_id": f"eq.{message_id}",
        "limit": "1"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return len(response.json()) > 0


def save_ready(message):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_ready"
    )

    payload = {
        "message_id": message["message_id"],
        "session_id": message["session_id"],
        "message_text": message["message_text"],
        "last_btn": message["last_btn"],
        "status": "pending"
    }

    response = requests.post(
        url,
        headers={
            **HEADERS,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        json=payload,
        timeout=10
    )

    response.raise_for_status()


# ========================================
# UPDATE QUEUE STATUS
# ========================================

def update_status(
    queue_id,
    status
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_queue"
    )

    params = {
        "id": f"eq.{queue_id}"
    }

    payload = {
        "status": status
    }

    response = requests.patch(
        url,
        headers={
            **HEADERS,
            "Content-Type": "application/json"
        },
        params=params,
        json=payload,
        timeout=10
    )

    response.raise_for_status()


# ========================================
# PROCESS ONE MESSAGE
# ========================================

def process_message(message):

    queue_id = message["id"]
    message_id = message["message_id"]
    session_id = message["session_id"]

    print(
        "🔎 SPECIALIST 2:",
        message_id,
        "| SESSION:",
        session_id
    )

    # ------------------------------------
    # Read ignore configuration
    # ------------------------------------

    ignore_types = get_ignore_types()

    print(
        "📋 IGNORE TYPES:",
        ignore_types
    )

    # ------------------------------------
    # Currently we only support CTN
    # ------------------------------------

    if "CTN" in ignore_types:

        ctn_event = get_ctn_event(
            session_id,
            message_id
        )

        if ctn_event:

            update_status(
                queue_id,
                "ignored"
            )

            print(
                "🚫 IGNORED — CTN:",
                ctn_event["value"],
                "| MESSAGE:",
                message_id
            )

            return

    # ------------------------------------
    # No ignore → send to READY
    # ------------------------------------

    if not ready_exists(message_id):

        save_ready(message)

        print(
            "✅ READY:",
            message_id,
            "| BTN:",
            message["last_btn"]
        )

    update_status(
        queue_id,
        "done"
    )


# ========================================
# MAIN LOOP
# ========================================

def main():

    print(
        "🧠 USER TEXT SPECIALIST 2 STARTED"
    )

    while True:

        try:

            messages = get_pending_messages()

            for message in messages:

                try:

                    update_status(
                        message["id"],
                        "processing"
                    )

                    process_message(message)

                except Exception as e:

                    print(
                        "🔴 MESSAGE ERROR:",
                        message["id"],
                        e
                    )

                    update_status(
                        message["id"],
                        "pending"
                    )

            time.sleep(2)

        except Exception as e:

            print(
                "🔴 SPECIALIST 2 ERROR:",
                e
            )

            time.sleep(5)


if __name__ == "__main__":
    main()