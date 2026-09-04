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
# TEMPLATE
# ========================================

TEMPLATE_URL = (
    BASE +
    "Service/user_text_viewer/user_text_00001"
)


# ========================================
# GET RESULT 1
# ========================================

def get_result1(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result1"
    )

    params = {
        "select": "message_id,session_id,answer,status",
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

    data = response.json()

    if not data:
        return None

    return data[0]


# ========================================
# GET RESULT 2
# ========================================

def get_result2(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result2"
    )

    params = {
        "select": (
            "message_id,session_id,"
            "btn,start_btn,end_btn,status"
        ),
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

    data = response.json()

    if not data:
        return None

    return data[0]


# ========================================
# GET TEMPLATE
# ========================================

def get_template():

    response = requests.get(
        TEMPLATE_URL,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ========================================
# GET RESULT MESSAGES
# ========================================

def get_pending_result1():

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result1"
    )

    params = {
        "select": (
            "id,message_id,session_id,"
            "answer,status"
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
# CHECK PAGE EXISTS
# ========================================

def page_exists(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_page"
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


# ========================================
# BUILD PAGE
# ========================================

def build_page(
    template,
    result1,
    result2
):

    page = {
        "engine": "page",
        "title": template.get(
            "title",
            ""
        ),
        "messages": [
            result1["answer"]
        ],
        "buttons": []
    }

    # ------------------------------------
    # TEMPLATE BUTTONS
    # ------------------------------------

    template_buttons = template.get(
        "buttons",
        []
    )

    for button in template_buttons:

        button_type = button.get(
            "type"
        )

        # START
        if button_type == "start":

            page["buttons"].append({
                "id": result2["start_btn"],
                "text": button.get(
                    "text",
                    ""
                )
            })

        # END
        elif button_type == "end":

            page["buttons"].append({
                "id": result2["end_btn"],
                "text": button.get(
                    "text",
                    ""
                )
            })

        # CUSTOM
        elif button_type == "custom":

            page["buttons"].append({
                "id": button.get(
                    "id",
                    ""
                ),
                "text": button.get(
                    "text",
                    ""
                )
            })

    return page


# ========================================
# SAVE PAGE
# ========================================

def save_page(
    result1,
    page
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_page"
    )

    payload = {
        "message_id": result1["message_id"],
        "session_id": result1["session_id"],
        "page": page,
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
# UPDATE RESULT 1 STATUS
# ========================================

def update_result1_status(
    result1_id,
    status
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result1"
    )

    params = {
        "id": f"eq.{result1_id}"
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
# PROCESS
# ========================================

def process_message(result1):

    message_id = result1["message_id"]
    session_id = result1["session_id"]

    print(
        "🔎 SPECIALIST 5:",
        message_id,
        "| SESSION:",
        session_id
    )

    # ------------------------------------
    # DUPLICATE PROTECTION
    # ------------------------------------

    if page_exists(message_id):

        update_result1_status(
            result1["id"],
            "done"
        )

        print(
            "⚠️ PAGE ALREADY EXISTS:",
            message_id
        )

        return

    # ------------------------------------
    # RESULT 2
    # ------------------------------------

    result2 = get_result2(
        message_id
    )

    if not result2:

        print(
            "⏳ RESULT 2 NOT READY:",
            message_id
        )

        update_result1_status(
            result1["id"],
            "pending"
        )

        return

    # ------------------------------------
    # TEMPLATE
    # ------------------------------------

    template = get_template()

    # ------------------------------------
    # BUILD PAGE
    # ------------------------------------

    page = build_page(
        template,
        result1,
        result2
    )

    # ------------------------------------
    # SAVE
    # ------------------------------------

    save_page(
        result1,
        page
    )

    update_result1_status(
        result1["id"],
        "done"
    )

    print(
        "✅ PAGE READY:",
        message_id,
        "| SESSION:",
        session_id
    )

    print(
        page
    )


# ========================================
# MAIN
# ========================================

def main():

    print(
        "🧠 USER TEXT SPECIALIST 5 STARTED"
    )

    while True:

        try:

            messages = get_pending_result1()

            for message in messages:

                try:

                    update_result1_status(
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

                    update_result1_status(
                        message["id"],
                        "pending"
                    )

            time.sleep(2)

        except Exception as e:

            print(
                "🔴 SPECIALIST 5 ERROR:",
                e
            )

            time.sleep(5)


if __name__ == "__main__":
    main()