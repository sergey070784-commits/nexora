import requests
from datetime import datetime
import json
import time
from Core.page_engine import get_page
from Core.event_logger import send_event
import threading
from Core.check_commands import check_commands
from Core.calendar_engine import (
    get_calendar,
    get_calendar_events
)
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

from Core.gallery_router import get_gallery_data

from Core.gallery_show_wa import show_gallery_wa
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
contact_last_id = 0

# ========================================
# CONTACT FAST NAVIGATION
# ========================================
contact_page_cache = {}
page_cache = {}

def prefetch_contact_page(ctn_id):
    if not ctn_id or not ctn_id.startswith("CTN_") or ctn_id in contact_page_cache:
        return
    def _load():
        try:
            data = get_contact_data(ctn_id)
            if data:
                contact_page_cache[ctn_id] = data
                print("⚡ CONTACT PREFETCH READY:", ctn_id)
        except Exception as e:
            print("CONTACT PREFETCH ERROR:", ctn_id, e)
    threading.Thread(target=_load, daemon=True).start()

def get_fast_contact_data(ctn_id):
    data = contact_page_cache.pop(ctn_id, None)
    if data:
        print("⚡ CONTACT CACHE HIT:", ctn_id)
        return data
    print("⏳ CONTACT CACHE MISS:", ctn_id)
    return get_contact_data(ctn_id)

def prefetch_page(page_id):
    if not page_id or page_id in page_cache:
        return
    def _load():
        try:
            data = get_page(page_id)
            if data:
                page_cache[page_id] = data
                print("⚡ PAGE PREFETCH READY:", page_id)
        except Exception as e:
            print("PAGE PREFETCH ERROR:", page_id, e)
    threading.Thread(target=_load, daemon=True).start()

def get_fast_page(page_id):
    data = page_cache.pop(page_id, None)
    if data:
        print("⚡ PAGE CACHE HIT:", page_id)
        return data
    print("⏳ PAGE CACHE MISS:", page_id)
    return get_page(page_id)

def send_event_background(**kwargs):
    threading.Thread(target=send_event, kwargs=kwargs, daemon=True).start()

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

bot_config = requests.get(
    BASE + "Core/whatsapp_bot1_config.json",
    timeout=10
).json()

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
                    "bot": "eq.whatsapp_bot1",
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
def check_file_messages():

    global file_last_id

    while True:

        try:

            response = requests.get(

                f"{SUPABASE_URL}/rest/v1/file_messages",

                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                },

                params={
                    "select": "*",
                    "id": f"gt.{file_last_id}",
                    "target_bot": f"eq.{bot_config['bot']}",
                    "status": "eq.new",
                    "order": "id.asc"
                },

                timeout=10
            )

            if response.status_code != 200:

                print(
                    "🔴 WA FILE MESSAGE ERROR:",
                    response.status_code,
                    response.text
                )

                time.sleep(2)

                continue

            rows = response.json()

            for row in rows:

                file_last_id = row["id"]

                print()
                print("📥 WA FILE MESSAGE FOR BOT")

                print(
                    "SOURCE:",
                    row["source_bot"]
                )

                print(
                    "TARGET:",
                    row["target_bot"]
                )

                print(
                    "ASSET:",
                    row["asset_id"]
                )

                print(
                    "SESSION:",
                    row["session_id"]
                )

                print(
                    "CHAT:",
                    row.get("chat_id")
                )

                chat_id = row.get("chat_id")

                if not chat_id:

                    print(
                        "⚠️ WA NO CHAT_ID"
                    )

                    continue

                asset_response = requests.get(

                    f"{SUPABASE_URL}/rest/v1/assets",

                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization":
                            f"Bearer {SUPABASE_KEY}"
                    },

                    params={
                        "select": "*",
                        "asset_id":
                            f"eq.{row['asset_id']}",
                        "limit": 1
                    },

                    timeout=10
                )

                if asset_response.status_code != 200:

                    print(
                        "🔴 WA ASSET ERROR:",
                        asset_response.status_code
                    )

                    continue

                assets = asset_response.json()

                if not assets:

                    print(
                        "⚠️ WA ASSET NOT FOUND"
                    )

                    continue

                asset = assets[0]

                print(
                    "FILE:",
                    asset["file_name"]
                )

                print(
                    "URL:",
                    asset["cloudinary_url"]
                )

                try:

                    send_file(
                        chat_id,
                        asset["cloudinary_url"],
                        asset["file_name"]
                    )

                    requests.patch(

                        f"{SUPABASE_URL}/rest/v1/file_messages",

                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization":
                                f"Bearer {SUPABASE_KEY}",
                            "Content-Type":
                                "application/json"
                        },

                        params={
                            "id": f"eq.{row['id']}"
                        },

                        json={
                            "status": "sent"
                        },

                        timeout=10
                    )

                    print(
                        "✅ WA FILE SENT TO USER"
                    )

                except Exception as e:

                    print(
                        "🔴 WA SEND FILE ERROR:",
                        e
                    )

                    requests.patch(

                        f"{SUPABASE_URL}/rest/v1/file_messages",

                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization":
                                f"Bearer {SUPABASE_KEY}",
                            "Content-Type":
                                "application/json"
                        },

                        params={
                            "id": f"eq.{row['id']}"
                        },

                        json={
                            "status": "error"
                        },

                        timeout=10
                    )

        except Exception as e:

            print(
                "🔴 WA FILE MESSAGE WORKER ERROR:",
                e
            )

        time.sleep(1)


def send_file(
    chat_id,
    file_url,
    file_name
):

    url = (
        f"{API_URL}/sendFileByUrl/{API_TOKEN}"
    )

    payload = {
        "chatId": chat_id,
        "urlFile": file_url,
        "fileName": file_name
    }

    response = requests.post(
        url,
        json=payload
    )

    return response.json()

file_last_id = 0

    
print("🟢 wa demo_lead 1  Running...")

#===== MAIN LOOP =====

# CONTACT NAVIGATION WORKER DISABLED — fast session path active
# CTN navigation is handled directly from the current session contact_data.

threading.Thread(
    target=check_file_messages,
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
        if message_data.get(
            "typeMessage"
        ) == "imageMessage":
            

            file_data = (
                message_data.get(
                    "fileMessageData"
                ) or {}
            )

            file_url = file_data.get(
                "downloadUrl"
            )

            file_name = file_data.get(
                "fileName"
            )

            mime_type = file_data.get(
                "mimeType"
            )

            print()
            print("📥 WA FILE RECEIVED")
            print("SESSION:", sender)
            print("FILE:", file_name)
            print("MIME:", mime_type)
            print("URL:", file_url)

            data = {

                "session_id": sender,

                "source_bot": bot_config["bot"],

                "channel": "whatsapp",

                "chat_id": sender,

                "file_name": file_name,

                "file_type": "image",

                "file_url": file_url,

                "status": "new"
            }

            response = requests.post(

                f"{SUPABASE_URL}/rest/v1/file_events",

                headers={
                    **HEADERS,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },

                json=data,

                timeout=10
            )

            if response.status_code in (200, 201):

                print()
                print("🟢 WA FILE EVENT CREATED")
                print("FILE:", file_name)
                print("TYPE:", "image")
                print("SESSION:", sender)

            else:

                print()
                print(
                    "🔴 WA FILE EVENT ERROR:",
                    response.status_code,
                    response.text
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
               
            elif sender in user_data:

                state = user_data.get(sender)

                btn_id = state["buttons"].get(text, text)

                if str(state.get("page") or "").startswith("CTN_") and state.get("contact_mode"):

                    contact_data = state.get("contact_data") or {}
                    field = contact_data.get("field")
                    next_id = contact_data.get("next")

                    if field and next_id:
                        # Save memory asynchronously; navigation never waits for it.
                        send_event_background(
                            bot_config=bot_config,
                            session_id=sender,
                            value=f"{field}={text}"
                        )

                        if next_id.startswith("CTN_"):
                            data = get_fast_contact_data(next_id)
                            if data:
                                state["page"] = data.get("id")
                                state["buttons"] = {}
                                state["contact_mode"] = True
                                state["contact_data"] = data
                                user_data[sender] = state
                                show_contact(sender, data)

                                next_next = data.get("next")
                                if next_next and next_next.startswith("CTN_"):
                                    prefetch_contact_page(next_next)
                                elif next_next and next_next.startswith("BTN_"):
                                    prefetch_page(next_next)

                            delete_notification(receipt_id)
                            continue

                        if next_id.startswith("BTN_"):
                            # Command routing is asynchronous; send the BTN route key.
                            send_event_background(
                                bot_config=bot_config,
                                session_id=sender,
                                value=next_id
                            )

                            data = get_fast_page(next_id)
                            if data:
                                show_page(sender, data)

                            state["contact_mode"] = False
                            state["contact_data"] = None
                            state["page"] = None
                            user_data[sender] = state

                            delete_notification(receipt_id)
                            continue

                if not btn_id:

                    send_event_background(
                        bot_config=bot_config,
                        session_id=sender,
                        message=text
                    )

                else:

                    if btn_id.startswith("CTN_"):

                        print()
                        print("📋 CONTACT BUTTON")
                        print("CTN:", btn_id)

                        send_event_background(
                            bot_config=bot_config,
                            session_id=sender,
                            value=btn_id
                        )

                        data = get_fast_contact_data(
                            btn_id
                        )

                        if data:

                            state["page"] = data.get("id")
                            state["buttons"] = {}
                            state["contact_mode"] = True
                            state["contact_data"] = data

                            user_data[sender] = state

                            show_contact(
                                sender,
                                data
                            )

                            next_id = data.get("next")
                            if next_id and next_id.startswith("CTN_"):
                                prefetch_contact_page(next_id)
                            elif next_id and next_id.startswith("BTN_"):
                                prefetch_page(next_id)

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

                            events = get_calendar_events()

                            if len(events) >= 2:

                                save_values(
                                    user_data,
                                    sender,
                                    {
                                        events[0]: date,
                                        events[1]: selected_time
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
                    if btn_id.startswith("GRL_"):

                        print()
                        print("🖼 WA GALLERY BUTTON")
                        print("GRL:", btn_id)

                        data = get_gallery_data(
                            btn_id
                        )

                        if not data:

                            print(
                                "🔴 WA GALLERY DATA NOT FOUND:",
                                btn_id
                            )

                            delete_notification(
                                receipt_id
                            )

                            continue

                        gallery = show_gallery_wa(
                            sender,
                            data
                        )

                        if not gallery:

                            print(
                                "🔴 WA GALLERY RESULT EMPTY:",
                                btn_id
                            )

                            delete_notification(
                                receipt_id
                            )

                            continue

                        # ========================================
                        # SHOW GALLERY IMAGES IN WA
                        # ========================================

                        for item in gallery.get(
                            "items",
                            []
                        ):

                            if item.get("type") != "image":
                                continue

                            image_url = item.get(
                                "url"
                            )

                            if not image_url:
                                continue

                            print()
                            print(
                                "🖼 WA GALLERY SEND IMAGE"
                            )
                            print(
                                "URL:",
                                image_url
                            )

                            send_image(
                                sender,
                                image_url
                            )

                        # ========================================
                        # SAVE GALLERY BUTTONS
                        # ========================================

                        state = user_data.get(
                            sender,
                            {}
                        )

                        state["buttons"] = gallery.get(
                            "buttons",
                            {}
                        )

                        state["gallery_actions"] = gallery.get(
                            "gallery_actions",
                            {}
                        )

                        user_data[sender] = state

                        print()
                        print(
                            "🖼 WA GALLERY BUTTONS:",
                            state["buttons"]
                        )

                        print(
                            "🖼 WA GALLERY ACTIONS:",
                            state["gallery_actions"]
                        )

                        # ========================================
                        # SHOW GALLERY ACTION BUTTONS
                        # ========================================

                        buttons = []

                        for action in gallery.get(
                            "actions",
                            []
                        ):

                            if not action.get("id"):
                                continue

                            if not action.get("text"):
                                continue

                            buttons.append(
                                {
                                    "buttonId":
                                        action["id"],

                                    "buttonText":
                                        action["text"]
                                }
                            )

                        if buttons:

                            print()
                            print(
                                "🖼 WA GALLERY SEND BUTTONS:",
                                buttons
                            )

                            send_reply_buttons(
                                sender,
                                buttons
                            )

                        delete_notification(
                            receipt_id
                        )

                        continue
                    # ========================================
                    # GALLERY FILE ACTION
                    # ========================================

                    gallery_actions = user_data.get(
                        sender,
                        {}
                    ).get(
                        "gallery_actions",
                        {}
                    )

                    action = gallery_actions.get(
                        btn_id
                    )

                    if action and action.get("type") == "file":

                        print()
                        print("📄 WA GALLERY FILE ACTION")
                        print("FILE ID:", btn_id)
                        print("ACTION:", action)

                        file_url = action.get(
                            "file_url"
                        )

                        if not file_url:

                            print(
                                "🔴 WA GALLERY FILE URL NOT FOUND:",
                                btn_id
                            )

                            delete_notification(
                                receipt_id
                            )

                            continue

                        file_name = action.get(
                            "display_name",
                            f"{btn_id}.pdf"
                        )

                        if file_name.lower().endswith(".pdf"):

                            file_type = "document"

                        else:

                            file_type = "image"

                        data = {

                            "session_id": sender,

                            "source_bot":
                                bot_config["bot"],

                            "channel":
                                "whatsapp",

                            "chat_id":
                                sender,

                            "file_name":
                                file_name,

                            "file_type":
                                file_type,

                            "file_url":
                                file_url,

                            "cloudinary_public_id":
                                action.get(
                                    "public_id"
                                ),

                            "file_source":
                                "gallery",

                            "status":
                                "new"
                        }

                        response = requests.post(

                            f"{SUPABASE_URL}/rest/v1/file_events",

                            headers={
                                "apikey":
                                    SUPABASE_KEY,

                                "Authorization":
                                    f"Bearer {SUPABASE_KEY}",

                                "Content-Type":
                                    "application/json",

                                "Prefer":
                                    "return=minimal"
                            },

                            json=data,

                            timeout=10
                        )

                        if response.status_code in (200, 201):

                            print()
                            print(
                                "📤 WA GALLERY FILE EVENT CREATED"
                            )

                            print(
                                "FILE:",
                                file_name
                            )

                            print(
                                "TYPE:",
                                file_type
                            )

                            print(
                                "URL:",
                                file_url
                            )
                            # ========================================
                            # KEEP GALLERY BUTTONS AFTER FILE SEND
                            # ========================================

                            state = user_data.get(
                                sender,
                                {}
                            )

                            buttons = []

                            for text, button_id in state.get(
                                "buttons",
                                {}
                            ).items():

                                buttons.append(
                                    {
                                        "buttonId": button_id,
                                        "buttonText": text
                                    }
                                )

                            if buttons:

                                print()
                                print(
                                    "🖼 WA GALLERY KEEP BUTTONS:",
                                    buttons
                                )

                                send_reply_buttons(
                                    sender,
                                    buttons
                                )

                        else:

                            print()
                            print(
                                "🔴 WA GALLERY FILE EVENT ERROR:",
                                response.status_code,
                                response.text
                            )

                        delete_notification(
                            receipt_id
                        )

                        continue


                    # ========================================
                    # NORMAL PAGE
                    # ========================================

                    data = get_page(
                        btn_id
                    )

                    if data:

                        engine = data.get(
                            "engine",
                            "page"
                        )

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
