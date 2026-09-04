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
# MESSAGE TIME
# ========================================

def get_message_created_at(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_messages"
    )

    params = {
        "select": "created_at",
        "id": f"eq.{message_id}",
        "limit": "1"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return data[0]["created_at"]


# ========================================
# GET LAST CTN
# ========================================

def get_last_ctn(
    session_id,
    message_created_at
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "events"
    )

    params = {
        "select": "id,value,created_at",
        "session_id": f"eq.{session_id}",
        "value": "like.CTN_*",
        "created_at": f"lte.{message_created_at}",
        "order": "created_at.desc",
        "limit": "1"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    events = response.json()

    if not events:
        return None

    return events[0]


# ========================================
# GET LAST BTN
# ========================================

def get_last_btn(
    session_id,
    message_created_at
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "events"
    )

    params = {
        "select": "id,value,created_at",
        "session_id": f"eq.{session_id}",
        "value": "like.BTN_*",
        "created_at": f"lte.{message_created_at}",
        "order": "created_at.desc",
        "limit": "1"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    events = response.json()

    if not events:
        return None

    return events[0]


# ========================================
# CHECK ACTIVE CTN
# ========================================

def get_active_ctn(
    session_id,
    message_created_at
):

    last_ctn = get_last_ctn(
        session_id,
        message_created_at
    )

    if not last_ctn:
        return None

    last_btn = get_last_btn(
        session_id,
        message_created_at
    )

    # No BTN after CTN
    if not last_btn:
        return last_ctn

    ctn_time = last_ctn["created_at"]
    btn_time = last_btn["created_at"]

    # BTN happened after CTN
    if btn_time > ctn_time:

        print(
            "🔓 BTN AFTER CTN:",
            last_btn["value"],
            "| CTN:",
            last_ctn["value"]
        )

        return None

    # CTN is still active
    return last_ctn


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
        session_id,
        "| BTN:",
        message["last_btn"]
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
    # Get message time
    # ------------------------------------

    message_created_at = get_message_created_at(
        message_id
    )

    if not message_created_at:

        raise Exception(
            f"Message time not found: {message_id}"
        )

    # ------------------------------------
    # CTN CHECK
    # ------------------------------------

    if "CTN" in ignore_types:

        active_ctn = get_active_ctn(
            session_id,
            message_created_at
        )

        if active_ctn:

            update_status(
                queue_id,
                "ignored"
            )

            print(
                "🚫 IGNORED — ACTIVE CTN:",
                active_ctn["value"],
                "| MESSAGE:",
                message_id
            )

            return

    # ------------------------------------
    # No active ignore
    # → send to READY
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

                    process_message(
                        message
                    )

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