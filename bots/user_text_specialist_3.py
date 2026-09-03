import requests
import time
import re


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)


# =========================
# CONFIG
# =========================

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

RESPONSES_URL = (
    BASE + "pages/pickers/user_text_responses.json"
)


# =========================
# RESPONSE JSON
# =========================

def get_responses():
    response = requests.get(
        RESPONSES_URL,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# =========================
# READY QUEUE
# =========================

def get_pending_messages():

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_ready"
    )

    params = {
        "select": "id,message_id,session_id,message_text,status",
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


# =========================
# RESULT CHECK
# =========================

def result_exists(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result1"
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


# =========================
# LANGUAGE
# =========================

def detect_language(text):

    if re.search(r"[\u0590-\u05FF]", text):
        return "he"

    return "en"


# =========================
# NORMALIZE
# =========================

def normalize(text):

    text = text.strip().lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# =========================
# KEYWORD MATCH
# =========================

def keyword_matches(text, keyword, language):

    text = normalize(text)
    keyword = normalize(keyword)

    if not keyword:
        return False

    if language == "en":

        pattern = (
            r"\b"
            + re.escape(keyword)
            + r"\b"
        )

        return re.search(
            pattern,
            text,
            re.IGNORECASE
        ) is not None

    # Hebrew
    return keyword in text


# =========================
# FIND ANSWER
# =========================

def find_answer(message_text, data):

    language = detect_language(
        message_text
    )

    responses = data.get(
        "responses",
        []
    )

    # First search normal response categories
    for item in responses:

        if item.get("id") == "not_found":
            continue

        item_language = item.get(
            "language"
        )

        if item_language != language:
            continue

        keywords = item.get(
            "keywords",
            []
        )

        for keyword in keywords:

            if keyword_matches(
                message_text,
                keyword,
                language
            ):
                return item.get(
                    "answer"
                )

    # Not found
    for item in responses:

        if item.get("id") != "not_found":
            continue

        answers = item.get(
            "answers",
            {}
        )

        return answers.get(
            language,
            answers.get("en")
        )

    return None


# =========================
# SAVE RESULT
# =========================

def save_result(message, answer):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result1"
    )

    payload = {
        "message_id": message["message_id"],
        "session_id": message["session_id"],
        "message_text": message["message_text"],
        "answer": answer,
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


# =========================
# UPDATE READY STATUS
# =========================

def update_status(
    ready_id,
    status
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_ready"
    )

    params = {
        "id": f"eq.{ready_id}"
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


# =========================
# PROCESS ONE MESSAGE
# =========================

def process_message(message):

    ready_id = message["id"]
    message_id = message["message_id"]

    print(
        "🔎 SPECIALIST 3:",
        message_id,
        "| TEXT:",
        message["message_text"]
    )

    # Protection from duplicates
    if result_exists(message_id):

        update_status(
            ready_id,
            "done"
        )

        print(
            "⚠️ RESULT ALREADY EXISTS:",
            message_id
        )

        return

    # Load JSON dictionary
    data = get_responses()

    # Find answer
    answer = find_answer(
        message["message_text"],
        data
    )

    if not answer:
        print(
            "⚠️ NO ANSWER:",
            message_id
        )

        update_status(
            ready_id,
            "pending"
        )

        return

    # Save result
    save_result(
        message,
        answer
    )

    # Mark source message as done
    update_status(
        ready_id,
        "done"
    )

    print(
        "✅ RESULT 1:",
        message_id,
        "→",
        answer
    )


# =========================
# MAIN
# =========================

def main():

    print(
        "🧠 USER TEXT SPECIALIST 3 STARTED"
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
                "🔴 SPECIALIST 3 ERROR:",
                e
            )

            time.sleep(5)


if __name__ == "__main__":
    main()