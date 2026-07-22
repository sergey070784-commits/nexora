import time
import requests
import json

# ==========================
# НАСТРОЙКИ
# ==========================

BTN_DICTIONARY_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "pages/pickers/dictionary/btn_dictionary.json"
)

CONFIG_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Core/config.json"
)

config = requests.get(
    CONFIG_URL,
    timeout=10
).json()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

TABLE = "user_journal"
LEADS_TABLE = "leads"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

btn_dictionary = {}

last_dictionary_update = 0

last_id = 0
last_leads = {}
def init_last_id():

    global last_id

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{TABLE}",
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

    print(f"Start from ID {last_id}")


def load_btn_dictionary():

    global btn_dictionary
    global last_dictionary_update

    now = time.time()

    if now - last_dictionary_update < 1800:
        return

    try:

        response = requests.get(
            BTN_DICTIONARY_URL,
            timeout=10
        )

        if response.status_code == 200:

            btn_dictionary = response.json()

            last_dictionary_update = now

            print(
                f"Loaded {len(btn_dictionary)} BTN records"
            )

    except Exception as e:

        print(
            "Dictionary error:",
            e
        )
        print("Lead Processor started...\n")

init_last_id()
def save_lead(session_id, channel, lead):

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/{LEADS_TABLE}",

        headers=HEADERS,

        params={
            "select": "id",
            "session_id": f"eq.{session_id}",
            "limit": 1
        },

        timeout=10

    )

    if response.status_code != 200:
        print("Lead lookup failed")
        return

    rows = response.json()

    data = {
        "session_id": session_id,
        "channel": channel,
        "lead_json": lead
    }

    if rows:

        lead_id = rows[0]["id"]

        response = requests.patch(

            f"{SUPABASE_URL}/rest/v1/{LEADS_TABLE}?id=eq.{lead_id}",

            headers={
                **HEADERS,
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },

            json=data,

            timeout=10

        )

        if response.status_code in (200, 204):
            print("Lead updated")

        else:
            print("Update failed:", response.text)

    else:

        response = requests.post(

            f"{SUPABASE_URL}/rest/v1/{LEADS_TABLE}",

            headers={
                **HEADERS,
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },

            json=data,

            timeout=10

        )

        if response.status_code in (200, 201):
            print("Lead created")

        else:
            print("Insert failed:", response.text)
while True:

    load_btn_dictionary()

    try:

        response = requests.get(

            f"{SUPABASE_URL}/rest/v1/{TABLE}",

            headers=HEADERS,

            params={
                "select": "*",
                "id": f"gt.{last_id}",
                "order": "id.asc"
            },

            timeout=10

        )

        if response.status_code == 200:

            rows = response.json()

            for row in rows:

                last_id = row["id"]

                print(
                    f"ID={row['id']}  Session={row['session_id']}"
                )
                lead = {}

                actions = row.get("actions", [])

                for action in actions:

                    if action.get("event") != "button_click":
                        continue

                    button = action.get("value")

                    if button not in btn_dictionary:
                        continue

                    item = btn_dictionary[button]

                    lead[item["field"]] = item["value"]

                if not lead:
                    continue

                lead_key = json.dumps(
                    lead,
                    sort_keys=True,
                    ensure_ascii=False
                )

                session = row["session_id"]

                if last_leads.get(session) == lead_key:
                    continue

                last_leads[session] = lead_key

                print(
                    json.dumps(
                        lead,
                        indent=4,
                        ensure_ascii=False
                    )
                )
                save_lead(
                    row["session_id"],
                    row["channel"],
                    lead
                )
        else:

            print(
                "Supabase error:",
                response.status_code
            )

            print(response.text)

    except Exception as e:

        print(
            "ERROR:",
            e
        )

    time.sleep(1)