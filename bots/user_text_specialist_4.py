import requests
import time


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


SCENARIOS_URL = (
    BASE + "pages/pickers/user_text_scenarios.json"
)


# =========================
# SCENARIO JSON
# =========================

def get_scenarios():

    response = requests.get(
        SCENARIOS_URL,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data.get("scenarios", [])


# =========================
# READY TABLE
# =========================

def get_pending_messages():

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_specialist_ready"
    )

    params = {
        "select": "id,message_id,session_id,message_text,last_btn,status",
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
# MESSAGE TIME
# =========================

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


# =========================
# FIND SCENARIO BY BTN
# =========================

def find_scenario_by_btn(btn, scenarios):

    if not btn:
        return None

    if not btn.startswith("BTN_"):
        return None

    try:
        btn_number = int(
            btn.replace("BTN_", "")
        )
    except ValueError:
        return None

    for scenario in scenarios:

        start_btn = scenario.get("start_btn")
        end_btn = scenario.get("end_btn")

        if not start_btn or not end_btn:
            continue

        try:
            start_number = int(
                start_btn.replace("BTN_", "")
            )

            end_number = int(
                end_btn.replace("BTN_", "")
            )

        except ValueError:
            continue

        if (
            start_number
            <= btn_number
            <= end_number
        ):
            return scenario

    return None


# =========================
# FIND LAST ENTRY
# =========================

def get_last_entry(session_id, message_created_at):

    if not message_created_at:
        return None

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "events"
    )

    params = {
        "select": "id,value,created_at",
        "session_id": f"eq.{session_id}",
        "created_at": f"lte.{message_created_at}",
        "order": "created_at.desc",
        "limit": "50"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    events = response.json()

    for event in events:

        value = event.get("value")

        if not value:
            continue

        # Telegram ENTRY
        if value.startswith("/start "):

            entry_id = value[
                len("/start "):
            ].strip()

            if entry_id.startswith("nx_"):
                return entry_id

        # WhatsApp ENTRY
        if value.startswith("nx_"):

            return value.strip()

    return None


# =========================
# FIND SCENARIO BY ENTRY
# =========================

def find_scenario_by_entry(
    entry_id,
    scenarios
):

    if not entry_id:
        return None

    for scenario in scenarios:

        if scenario.get("id") == entry_id:
            return scenario

    return None


# =========================
# RESULT CHECK
# =========================

def result_exists(message_id):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result2"
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
# SAVE RESULT
# =========================

def save_result(
    message,
    btn,
    scenario
):

    url = (
        f"{SUPABASE_URL}/rest/v1/"
        "user_text_result2"
    )

    payload = {
        "message_id": message["message_id"],
        "session_id": message["session_id"],
        "btn": btn,
        "start_btn": scenario["start_btn"],
        "end_btn": scenario["end_btn"],
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
    session_id = message["session_id"]
    message_text = message["message_text"]
    last_btn = message["last_btn"]

    # =========================
    # IGNORE NX_ TEXT
    # =========================

    if "nx_" in message_text:

        update_status(
            ready_id,
            "done"
        )

        print(
            "⏭️ IGNORE NX_ TEXT:",
            message_id,
            "| TEXT:",
            message_text
        )

        return

    print(
        "🔎 SPECIALIST 4:",
        message_id,
        "| SESSION:",
        session_id,
        "| BTN:",
        last_btn
    )

    # -------------------------
    # DUPLICATE PROTECTION
    # -------------------------

    if result_exists(message_id):

        update_status(
            ready_id,
            "done"
        )

        print(
            "⚠️ RESULT 2 ALREADY EXISTS:",
            message_id
        )

        return

    # -------------------------
    # LOAD SCENARIOS
    # -------------------------

    scenarios = get_scenarios()

    # -------------------------
    # FIRST: TRY BTN
    # -------------------------

    scenario = find_scenario_by_btn(
        last_btn,
        scenarios
    )

    if scenario:

        save_result(
            message,
            last_btn,
            scenario
        )

        update_status(
            ready_id,
            "done"
        )

        print(
            "✅ RESULT 2 BY BTN:",
            message_id,
            "| SESSION:",
            session_id,
            "| BTN:",
            last_btn,
            "| SCENARIO:",
            scenario["id"],
            "| START:",
            scenario["start_btn"],
            "| END:",
            scenario["end_btn"]
        )

        return

    # -------------------------
    # SECOND: TRY ENTRY
    # -------------------------

    print(
        "🔍 BTN NOT FOUND → CHECK ENTRY:",
        message_id
    )

    message_created_at = get_message_created_at(
        message_id
    )

    entry_id = get_last_entry(
        session_id,
        message_created_at
    )

    print(
        "🚪 LAST ENTRY:",
        entry_id
    )

    scenario = find_scenario_by_entry(
        entry_id,
        scenarios
    )

    if scenario:

        save_result(
            message,
            last_btn,
            scenario
        )

        update_status(
            ready_id,
            "done"
        )

        print(
            "✅ RESULT 2 BY ENTRY:",
            message_id,
            "| SESSION:",
            session_id,
            "| ENTRY:",
            entry_id,
            "| START:",
            scenario["start_btn"],
            "| END:",
            scenario["end_btn"]
        )

        return

    # -------------------------
    # NOTHING FOUND
    # -------------------------

    print(
        "⚠️ BTN AND ENTRY NOT FOUND:",
        message_id,
        "| SESSION:",
        session_id
    )

    update_status(
        ready_id,
        "done"
    )


# =========================
# MAIN
# =========================

def main():

    print(
        "🧠 USER TEXT SPECIALIST 4 STARTED"
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
                "🔴 SPECIALIST 4 ERROR:",
                e
            )

            time.sleep(5)


if __name__ == "__main__":
    main()