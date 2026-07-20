import requests
from datetime import datetime
import json
import time
#===== GREEN API =====

ID_INSTANCE = "7107624116"
API_TOKEN = "7343f694bbfd4f6a9d8c7dd48934073e46cd9c9a44b04428bc"

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
    channel="whatsapp"
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

                "channel": "whatsapp",

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

    track_event(
        chat_id,
        "page_open",
        page,
        "whatsapp"
    )

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

#===== MAIN LOOP =====
print("🟢 Nexora Leads 1 Engine Running...")

while True:

    try:

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

                if text.lower() in [
                    "lead",
                    "start",
                    "menu"
                ]:

                    log_message(
                    sender,
                        text
                    )

                    show_page(
                        sender,
                        "page.tools"
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

                        page_id = routes[
                            button_id
                        ]

                        page = pages[
                            page_id
                        ]

                        show_page(
                            sender,
                            page
                        )

                    else:

                        log_message(
                            sender,
                            text
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
