import requests
from datetime import datetime
import json
import time
from Core.page_engine import get_page
from Core.event_logger import send_event
import threading
from Core.check_commands import check_commands
from Core.calendar_engine import get_calendar

from Core.value_engine import (
    save_values,
    get_values,
    send_values
)
#===== GREEN API =====

ID_INSTANCE = "7107624116"
API_TOKEN = "7343f694bbfd4f6a9d8c7dd48934073e46cd9c9a44b04428bc"

API_URL = (
    f"https://api.green-api.com/"
    f"waInstance{ID_INSTANCE}"
    )
#===== USER DATA =====

user_data = {}
ignore_messages = {}
BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

bot_config = requests.get(
    BASE + "Core/whatsapp_bot1_config.json",
    timeout=10
).json()

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
    
print("🟢 wa demo_lead 1  Running...")

#===== MAIN LOOP =====
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
               
            elif sender in user_data:

                state = user_data.get(sender)

                btn_id = state["buttons"].get(text, text)
                
                if not btn_id:

                    send_event(
                        bot_config,
                        sender,
                        message=text
                    )

                else:

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
