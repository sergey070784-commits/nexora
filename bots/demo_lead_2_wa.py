import requests
from datetime import datetime
import json
import time
#===== GREEN API =====

ID_INSTANCE = "710722689636"
API_TOKEN = "b3d9f866e87744bbb18b90dc634b68f022a799d956034309bf"

API_URL = (
    f"https://api.green-api.com/"
    f"waInstance{ID_INSTANCE}"
    )
#===== USER DATA =====

user_data = {}

#===== SEND MESSAGE =====
routes = requests.get(
    "https://raw.githubusercontent.com/sergey070784-commits/nexora/main/navigation/routes.json"
).json()

pages = requests.get(
    "https://raw.githubusercontent.com/sergey070784-commits/nexora/main/navigation/pages.json"
).json()
popup_routes = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/navigation/popup_routes.json"
).json()
config = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/Core/config.json"
).json()
entry_points = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/navigation/entry_points.json"
).json()
bot_config = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/Core/whatsapp_bot2_config.json"
).json()
SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]
def send_message(chat_id, text):

    url = f"{API_URL}/sendMessage/{API_TOKEN}"

    payload = {
        "chatId": chat_id,
        "message": text
    }

    response = requests.post(
        url,
        json=payload
    )

    return response.json()

#===== GET NOTIFICATION =====
def send_image(chat_id, image_url):

    url = (
        f"{API_URL}/sendFileByUrl/{API_TOKEN}"
    )

    payload = {
        "chatId": chat_id,
        "urlFile": image_url,
        "fileName": "image.png"
    }

    response = requests.post(
        url,
        json=payload
    )

    return response.json()

def get_notification():

    url = (
        f"{API_URL}/receiveNotification/"
        f"{API_TOKEN}"
    )

    response = requests.get(url)

    if not response.text.strip():
        return None

    return response.json()

#===== DELETE NOTIFICATION =====

def delete_notification(receipt_id):

    url = (
        f"{API_URL}/deleteNotification/"
        f"{API_TOKEN}/{receipt_id}"
    )

    requests.delete(url)
def load_page(page):

    url = (
        "https://raw.githubusercontent.com/"
        "sergey070784-commits/nexora/main/pages/"
        f"{page}"
    )

    response = requests.get(url)

    return response.json()
def load_popup(popup):

    url = (
        "https://raw.githubusercontent.com/"
        "sergey070784-commits/nexora/main/pages/"
        f"{popup}"
    )

    response = requests.get(url)

    return response.json()
def track_event(
    session_id,
    event,
    value,
    channel=bot_config["channel"]
):

    requests.post(
        "https://royal-shape-a489.sergey070784.workers.dev",
        json={
            "session_id":
                str(session_id),

            "timestamp":
                datetime.now()
                .isoformat(),

            "channel":
                channel,

            "event":
                event,

            "value":
                value
        }
    )
def log_message(session_id, text):

    try:

        requests.post(

            "https://message.sergey070784.workers.dev/",

            json={

                "session_id": str(session_id),

                "channel": bot_config["channel"],

                "message": text

            },

            timeout=10

        )

    except Exception as e:

        print(e)
def show_page(chat_id, page):

    user_data[chat_id] = {
        "page": page,
        "buttons": {}
    }

    data = load_page(page)

    text = data["title"]

    for msg in data["messages"]:

        text += "\n\n" + msg

    send_message(
        chat_id,
        text
    )

    buttons = []

    for button in data["buttons"]:

        user_data[chat_id][
            "buttons"
        ][
            button["text"]
        ] = button["id"]

        buttons.append(
            {
                "buttonId":
                    button["id"],

                "buttonText":
                    button["text"]
            }
        )

    send_reply_buttons(
        chat_id,
        buttons
    )
def show_popup(chat_id, popup):

    data = load_popup(popup)

    user_data[chat_id] = {
        "popup": popup,
        "buttons": {}
    }

    text = data["title"]

    for msg in data["messages"]:

        text += "\n\n" + msg

    if data.get("image"):

        send_image(
            chat_id,
            data["image"]
        )
    send_message(
        chat_id,
        text
    )

    buttons = []

    for button in data["buttons"]:

        user_data[chat_id][
            "buttons"
        ][
            button["text"]
        ] = button["id"]

        buttons.append(
            {
                "buttonId":
                    button["id"],

                "buttonText":
                    button["text"]
            }
        )

    send_reply_buttons(
        chat_id,
        buttons
    )
def show_lead(chat_id, page):

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/leads",

        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },

        params={

            "session_id": f"eq.{chat_id}",

            "select": "lead_json",

            "limit": 1

        },

        timeout=10

    )

    if response.status_code != 200:

        send_message(
            chat_id,
            "Lead loading error."
        )

        return

    rows = response.json()

    if not rows:

        send_message(
            chat_id,
            "Lead not found."
        )

        return

    lead = rows[0]["lead_json"]

    data = load_page(page)

    title = data.get("title", "")

    user_data[chat_id] = {
        "page": page,
        "buttons": {}
    }

    text = ""

    if title:
        text += title + "\n\n"

    for key, value in lead.items():
        text += f"{key}: {value}\n"

    send_message(
        chat_id,
        text
    )

    buttons = []

    for button in data["buttons"]:

        user_data[chat_id]["buttons"][button["text"]] = button["id"]

        buttons.append(
            {
                "buttonId": button["id"],
                "buttonText": button["text"]
            }
        )

    send_reply_buttons(
        chat_id,
        buttons
    )
def send_reply_buttons(chat_id, buttons):
    url = (
        f"{API_URL}/sendInteractiveButtonsReply/{API_TOKEN}"
    )

    payload = {
        "chatId": chat_id,
        "header": "Nexora",
        "body": " ",
        "footer": " ",
        "buttons": buttons
    }
    response = requests.post(
        url,
        json=payload
    )
def check_commands():

    try:

        response = requests.get(

            f"{SUPABASE_URL}/rest/v1/commands",

            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },

            params={
                "select": "*",
                "target_bot": f"eq.{bot_config['bot']}",
                "status": "eq.new",
                "order": "id.asc"
            },

            timeout=10

        )

        if response.status_code != 200:
            return

        commands = response.json()

        for command in commands:

            print("\n===== NEW COMMAND =====")
            print(command)
            print("=======================\n")

            data = load_page(
                command["page"]
            )

            page_type = data.get("type")

            if page_type == "lead":

                show_lead(
                    command["session_id"],
                    command["page"]
                )

            else:

                show_page(
                    command["session_id"],
                    command["page"]
                )

            requests.patch(

                f"{SUPABASE_URL}/rest/v1/commands?id=eq.{command['id']}",

                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },

                json={
                    "status": "done"
                }

            )

    except Exception as e:

        print("COMMAND ERROR:", e)
#===== MAIN LOOP =====
print("🟢 Nexora wa 2 Running...")

while True:

    try:
        check_commands()

        notification = get_notification()

        if not notification:

            time.sleep(1)

            continue

        receipt_id = notification.get(
            "receiptId"
        )

        body = notification.get(
            "body"
        ) or {}

        webhook_type = body.get(
            "typeWebhook"
        )

        sender = (
            body.get(
                "senderData"
            ) or {}
        ).get("chatId")


        message_data = (
            body.get(
                "messageData"
            ) or {}
        )
        text = (
            (
                message_data.get(
                    "textMessageData"
                ) or {}
            ).get("textMessage")
            or
            (
                message_data.get(
                    "extendedTextMessageData"
                ) or {}
            ).get("text")
        )
        if message_data.get(
            "typeMessage"
        ) == "interactiveButtonsResponse":

            text = (
                (
                    message_data.get(
                        "interactiveButtonsResponse"
                    ) or {}
                ).get("selectedId")
                or
                (
                    message_data.get(
                        "interactiveButtonsResponse"
                ) or {}
                ).get("selectedDisplayText")
            )

        if (
                sender
                and text
                and webhook_type ==
                    "incomingMessageReceived"
        ):

                text_key = text.lower()

                if text_key in entry_points:

                    log_message(
                        sender,
                        text
                    )

                    page_id = entry_points[text_key]

                    page = pages[page_id]

                    data = load_page(page)

                    page_type = data.get("type")

                    if page_type == "lead":

                        show_lead(
                            sender,
                            page
                        )

                    else:

                        show_page(
                            sender,
                            page
                         )

                elif sender in user_data:

                    button_id = text

                    if button_id in popup_routes:

                        popup = popup_routes[
                            button_id
                        ]

                        show_popup(
                            sender,
                            popup
                        )

                    elif button_id in routes:
                        track_event(
                            sender,
                            "button_click",
                            button_id,
                            "whatsapp"
                        )
                        page_id = routes[
                            button_id
                        ]

                        page = pages[
                            page_id
                        ]

                        data = load_page(page)

                        page_type = data.get("type")
                       
                        if page_type == "lead":

                            show_lead(
                                sender,
                                page
                            )

                        else:
  
                            show_page(
                                sender,
                                page
                            )

        delete_notification(
            receipt_id
        )

        time.sleep(1)

    except Exception as e:

        print(
            "🔴 Error:",
            e
        )
