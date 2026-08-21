import requests
from datetime import datetime
import json
import time
from Core.page_engine import get_page
from Core.event_logger import send_event
import threading
from Core.check_commands import check_commands
from Core.calendar_engine import get_calendar
from Core.contact_handler import (
    get_contact_data,
    show_contact
)
from Core.value_engine import (
    save_values,
    get_values,
    send_values
)
from Core.contact_handler import get_contact_data
#===== GREEN API =====

ID_INSTANCE = "710722689636"
API_TOKEN = "b3d9f866e87744bbb18b90dc634b68f022a799d956034309bf"

API_URL = (
    f"https://api.green-api.com/"
    f"waInstance{ID_INSTANCE}"
    )
#===== USER DATA =====

user_data = {}
ignore_messages = {}
contact_last_id = 0

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

bot_config = requests.get(
    BASE + "Core/whatsapp_bot2_config.json",
    timeout=10
).json()

config = requests.get(
    BASE + "Core/config.json",
    timeout=10
).json()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

#===== SEND MESSAGE =====

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
#===== get NOTIFICATION =====

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

def show_contact(chat_id, data):

    title = data.get(
        "title",
        ""
    )

    messages = data.get(
        "messages",
        []
    )

    text = title

    for message in messages:

        if text:
            text += "\n\n"

        text += message

    send_message(
        chat_id,
        text
    )

    print(
        "📋 CONTACT SHOWN:",
        data.get("id")
    )

def show_page(chat_id, data):
   
    state = user_data.get(chat_id, {})

    state["page"] = data.get("id")

    state["buttons"] = {}

    user_data[chat_id] = state

    text = data["title"]

    for msg in data["messages"]:

        text += "\n\n" + msg

    send_message(
        chat_id,
        text
    )

    buttons = []

    for button in data["buttons"]:

        user_data[chat_id]["buttons"][
            button["text"]
        ] = button["id"]

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
    
def show_popup(chat_id, data):

    state = user_data.get(chat_id, {})

    state["page"] = data.get("id")

    state["buttons"] = {}

    user_data[chat_id] = state

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
        
        "body": " ",
        
        "buttons": buttons
    }
    response = requests.post(
        url,
        json=payload
    )

def show_command(chat_id, data):

    print("SHOW COMMAND")

    show_page(
        chat_id,
        data
    )
def init_contact_last_id():

    global contact_last_id

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/events",

        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },

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
            contact_last_id = rows[0]["id"]

    print(
        "WA CONTACT NAV START FROM ID:",
        contact_last_id
    )


def check_contact_navigation():

    global contact_last_id

    while True:

        try:

            response = requests.get(

                f"{SUPABASE_URL}/rest/v1/events",

                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                },

                params={
                    "select": "*",
                    "id": f"gt.{contact_last_id}",
                    "bot": "eq.whatsapp_bot2",
                    "order": "id.asc"
                },

                timeout=10
            )

            if response.status_code != 200:

                print(
                    "🔴 WA CONTACT NAV ERROR:",
                    response.status_code,
                    response.text
                )

                time.sleep(1)
                continue

            rows = response.json()

            for event in rows:

                contact_last_id = event["id"]

                value = event.get("value")

                if not value:
                    continue

                if not value.startswith(
                    "CONTACT_NEXT:"
                ):
                    continue

                next_id = value.replace(
                    "CONTACT_NEXT:",
                    "",
                    1
                )

                session_id = str(
                    event.get("session_id")
                )

                print()
                print("📋 WA CONTACT NAVIGATION")
                print("SESSION:", session_id)
                print("NEXT:", next_id)

                # ====================================
                # NEXT CONTACT PAGE
                # ====================================

                if next_id.startswith(
                    "CTN_"
                ):

                    data = get_contact_data(
                        next_id
                    )

                    if not data:

                        print(
                            "🔴 WA CONTACT PAGE NOT FOUND:",
                            next_id
                        )

                        continue

                    show_contact(
                        session_id,
                        data
                    )

                    print(
                        "📋 WA CONTACT NEXT PAGE SHOWN:",
                        next_id
                    )

                    continue

                # ====================================
                # CONTACT → NORMAL PAGE
                # ====================================

                if next_id.startswith(
                    "BTN_"
                ):

                    page = get_page(
                        next_id
                    )

                    if not page:

                        print(
                            "🔴 WA PAGE NOT FOUND:",
                            next_id
                        )

                        continue

                    print(
                        "➡️ WA CONTACT RETURN PAGE:",
                        next_id
                    )

                    show_page(
                        session_id,
                        page
                    )

                    print(
                        "📄 WA CONTACT RETURN PAGE SHOWN:",
                        next_id
                    )

        except Exception as e:

            print(
                "🔴 WA CONTACT NAV WORKER ERROR:",
                e
            )

        time.sleep(1)

    
print("🟢 wa demo_lead 2  Running...")

#===== MAIN LOOP =====

init_contact_last_id()

threading.Thread(
    target=check_contact_navigation,
    daemon=True
).start()

threading.Thread(
    target=check_commands,
    args=(
        bot_config,
        show_page,
        show_popup,
        show_command
    ),
    daemon=True
).start()

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

        if webhook_type != "incomingMessageReceived":

            delete_notification(receipt_id)

            continue

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
        print(
            "📦 WA MESSAGE DATA:",
            message_data
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

        elif message_data.get(
            "typeMessage"
        ) == "textMessage":

            text = (
                (
                    message_data.get(
                        "textMessageData"
                    ) or {}
                ).get("textMessage")
            )

        if (
            sender
            and text
            and webhook_type == "incomingMessageReceived"
        ):
           
            data = get_page(
                text.lower()
            )

            if data:

                send_event(
                    bot_config,
                    sender,
                    value=text.lower()
                )

                engine = data.get("engine", "page")

                if engine == "popup":

                    show_popup(
                        sender,
                        data
                    )

                elif engine == "calendar":

                    data = get_calendar(
                        config=data
                    )

                    show_page(
                        sender,
                        data
                    )

                else:

                    show_page(
                        sender,
                        data
                    )
                print("🔎 WA USER DATA KEYS:", list(user_data.keys()))
                print("🔎 WA SENDER:", repr(sender))
               
            elif sender in user_data:
                print(
                    "🔎 WA STATE CHECK:",
                    sender,
                    user_data.get(sender)
                )

                state = user_data.get(sender)

                btn_id = state["buttons"].get(text, text)

                if str(state.get("page") or "").startswith("CTN_"):

                    send_event(
                        bot_config,
                        sender,
                        message=text
                    )

                    print()
                    print("📥 CONTACT TEXT SENT")
                    print("SESSION:", sender)
                    print("TEXT:", text)

                    delete_notification(
                        receipt_id
                    )

                    continue
                
                if not btn_id:

                    send_event(
                        bot_config,
                        sender,
                        message=text
                    )

                else:

                    if btn_id.startswith("CTN_"):

                        print()
                        print("📋 CONTACT BUTTON")
                        print("CTN:", btn_id)

                        send_event(
                            bot_config,
                            sender,
                            value=btn_id
                        )

                        data = get_contact_data(
                            btn_id
                        )

                        if data:

                            state["page"] = data.get("id")
                            state["buttons"] = {}

                            user_data[sender] = state

                            show_contact(
                                sender,
                                data
                            )

                        delete_notification(
                            receipt_id
                        )

                        continue

                    if btn_id.startswith((
                        "CALENDAR_",
                        "MORNING_",
                        "AFTERNOON_",
                        "EVENING_",
                        "TIME_"
                    )):

                        if btn_id.startswith("TIME_"):

                            date, selected_time = btn_id.replace(
                                "TIME_",
                                ""
                            ).split("_")

                            save_values(

                                user_data,

                                sender,

                                {

                                    "APPOINTMENT_DATE": date,

                                    "APPOINTMENT_TIME": selected_time

                                }

                            )

                        data = get_calendar(
                            command=btn_id
                        )

                        show_page(
                            sender,
                            data
                        )
                        delete_notification(
                            receipt_id
                        )

                        continue

                    values = get_values(

                        user_data,

                        sender

                    )

                    if values:

                        send_values(

                            bot_config,

                            sender,

                            values

                        )

                    send_event(

                        bot_config,

                        sender,

                        value=btn_id

                    )

                    data = get_page(btn_id)

                    if data:

                        engine = data.get("engine", "page")

                        if engine == "popup":

                            show_popup(
                                sender,
                                data
                            )

                        elif engine == "calendar":

                            data = get_calendar(
                                config=data
                            )

                            show_page(
                                sender,
                                data
                            )

                        else:

                            show_page(
                                sender,
                                data
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
