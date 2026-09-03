import requests
import time


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
# SUPABASE HELPERS
# ========================================

def get_new_user_messages():

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_messages"
        "?select=id,session_id,message_text,created_at"
        "&order=id.asc"
        "&limit=20"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def queue_message_exists(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_queue"
        f"?select=id&message_id=eq.{message_id}"
        "&limit=1"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    return len(response.json()) > 0


def get_last_btn(session_id, message_created_at):

    url = (
        f"{SUPABASE_URL}/rest/v1/events"
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

    data = response.json()

    if not data:
        return None

    return data[0]["value"]


def save_to_queue(
    message_id,
    session_id,
    message_text,
    last_btn
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_queue"
    )

    payload = {
        "message_id": message_id,
        "session_id": str(session_id),
        "message_text": message_text,
        "last_btn": last_btn,
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
# SPECIALIST 1
# ========================================

def process_message(message):

    message_id = message["id"]
    session_id = message["session_id"]
    message_text = message["message_text"]
    message_created_at = message["created_at"]

    # Already processed by Specialist 1
    if queue_message_exists(message_id):
        return

    # Find the last BTN relevant to this message
    last_btn = get_last_btn(
        session_id,
        message_created_at
    )

    # Save result for the next specialists
    save_to_queue(
        message_id=message_id,
        session_id=session_id,
        message_text=message_text,
        last_btn=last_btn
    )

    print(
        "🧠 SPECIALIST 1 → QUEUE:",
        message_id,
        "| SESSION:",
        session_id,
        "| BTN:",
        last_btn
    )


# ========================================
# MAIN LOOP
# ========================================

def main():

    print("🧠 USER TEXT SPECIALIST 1 STARTED")

    while True:

        try:

            messages = get_new_user_messages()

            for message in messages:
                process_message(message)

            time.sleep(2)

        except Exception as e:

            print(
                "🔴 USER TEXT SPECIALIST ERROR:",
                e
            )

            time.sleep(5)


if __name__ == "__main__":
    main()