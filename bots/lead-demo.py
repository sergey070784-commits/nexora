import telebot
from telebot import types
import requests
from datetime import datetime
import time
import threading
from Core.page_engine import get_page
from Core.check_commands import check_commands
from Core.event_logger import send_event
from Core.calendar_engine import get_calendar
from Core.value_engine import (
    save_values,
    get_values,
    send_values
)
from Core.contact_handler import (
    get_contact_data,
    show_contact
)
from Core.gallery_router import get_gallery_data
from Core.gallery_show import show_gallery
from io import BytesIO
TOKEN = "8159696699:AAGOVnHtLK6ELCY32ctYxXFoH8qX6EvZbhc"

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8820758323

user_data = {}

FILE_MESSAGES_TABLE = "file_messages"

file_last_id = 0

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

bot_config = requests.get(
    BASE + "Core/bot1_config.json",
    timeout=10
).json()

config = requests.get(
    BASE + "Core/config.json",
    timeout=10
).json()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

def show_page(chat_id, data):
    import inspect

    print(
        "SHOW_PAGE:",
        data.get("title"),
        "CALLER:",
        inspect.stack()[1].function
    )

    state = user_data.get(chat_id, {})

    state["page"] = data.get("id")

    state["buttons"] = {

        button["text"]: button["id"]

        for button in data["buttons"]

    }

    user_data[chat_id] = state
    print("SHOW PAGE CHAT:", chat_id)
    print("SHOW PAGE BUTTONS:", state["buttons"])
    print("SHOW PAGE STATE:", state)

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    for button in data["buttons"]:

        keyboard.add(
            types.KeyboardButton(
                button["text"]
            )
        )

    text = data["title"]

    for msg in data["messages"]:

        text += "\n\n" + msg

    sent = bot.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )

    print(
        "TELEGRAM SENT:",
        sent.message_id,
        "TEXT:",
        sent.text,
        "KEYBOARD:",
        sent.reply_markup
    )
def show_popup(chat_id, data):

    state = user_data.get(chat_id, {})

    state["buttons"] = {

        button["text"]: button["id"]

        for button in data["buttons"]

    }

    user_data[chat_id] = state

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    for button in data["buttons"]:

        keyboard.add(
            types.KeyboardButton(
                button["text"]
            )
        )

    text = data["title"]

    for msg in data["messages"]:

        text += "\n\n" + msg

    try:

        if data.get("image"):

            bot.send_photo(
                chat_id,
                data["image"]
            )

    except Exception as e:

        print("PHOTO ERROR:", e)

    bot.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )
    
def show_command(chat_id, data):

    print("SHOW COMMAND")
    print("COMMAND BUTTONS:", data.get("buttons"))


    show_page(
        chat_id,
        data
    )

@bot.message_handler(commands=["start"])
def start(message):

    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:
        return

    entry_key = parts[1]
    send_event(

        bot_config,

        message.chat.id,

       value=message.text
    )
 
    data = get_page(entry_key)

    if not data:
        return

    show_page(
        message.chat.id,
        data
    )
@bot.message_handler(content_types=["document", "photo"])
def handle_file(message):

    chat_id = message.chat.id

    session_id = str(chat_id)

    file_name = None
    file_type = None
    file_id = None

    if message.document:

        file_id = message.document.file_id
        file_name = message.document.file_name
        file_type = "document"

    elif message.photo:

        file_id = message.photo[-1].file_id
        file_name = f"photo_{file_id}.jpg"
        file_type = "image"

    if not file_id:
        return

    print()
    print("📥 FILE RECEIVED")
    print("SESSION:", session_id)
    print("FILE:", file_name)
    print("TYPE:", file_type)

    try:

        file_info = bot.get_file(file_id)

        file_url = (
            f"https://api.telegram.org/file/bot"
            f"{TOKEN}/{file_info.file_path}"
        )

        data = {
            "session_id": session_id,
            "source_bot": bot_config["bot"],
            "channel": "telegram",
            "chat_id": str(chat_id),
            "file_name": file_name,
            "file_type": file_type,
            "file_url": file_url,
            "status": "new"
        }

        response = requests.post(

            f"{SUPABASE_URL}/rest/v1/file_events",

            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },

            json=data,

            timeout=10
        )

        if response.status_code in (200, 201):

            print("✅ FILE EVENT CREATED")

        else:

            print(
                "🔴 FILE EVENT ERROR:",
                response.status_code,
                response.text
            )

    except Exception as e:

        print(
            "🔴 FILE RECEIVE ERROR:",
            e
        )
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(
        "🔥 HANDLE MESSAGE:",
        repr(message.text),
        "CHAT:",
        message.chat.id
    )

    state = user_data.get(message.chat.id)
   
    if not state:
        return
    print("STATE OBJECT ID:", id(state))
    print("STATE BEFORE:", state)

    print("MESSAGE:", repr(message.text))
    print("STATE BUTTONS:", state.get("buttons"))
 
    btn_id = state["buttons"].get(message.text)
    print("🔘 PRESSED TEXT:", repr(message.text))
    print("🔑 BTN_ID:", repr(btn_id))

    if not btn_id:

        send_event(

            bot_config,

            message.chat.id,

            message=message.text

        )

        return

    if btn_id.startswith("CTN_"):

        contact_handler(
            bot=bot,
            chat_id=message.chat.id,
            btn_id=btn_id,
            user_data=user_data,
            bot_config=bot_config
        )

        return

    if btn_id.startswith((
        "CALENDAR_",
        "MORNING_",
        "AFTERNOON_",
        "EVENING_",
        "TIME_"
    )):

        if btn_id.startswith("TIME_"):

            date, time = btn_id.replace(
                "TIME_",
                ""
            ).split("_")

            save_values(

                user_data,

                message.chat.id,

                {

                    "APPOINTMENT_DATE": date,

                    "APPOINTMENT_TIME": time

                }

            )

        data = get_calendar(
            command=btn_id
        )

        show_page(
            message.chat.id,
            data
        )

        return

    values = get_values(

        user_data,

        message.chat.id

    )

    if values:

        send_values(

            bot_config,

            message.chat.id,

            values

        )

    send_event(

        bot_config,

        message.chat.id,

        value=btn_id

    )
    print("BTN_ID:", btn_id)

    if btn_id.startswith("CTN_"):

        print()
        print("📋 CONTACT BUTTON")
        print("CTN:", btn_id)

        data = get_contact_data(
            btn_id
        )

        if not data:
            return

        show_contact(
            bot,
            message.chat.id,
            data
        )

        return

    if btn_id.startswith("GRL_"):

        data = get_gallery_data(btn_id)

        if not data:
            return

        show_gallery(
            bot,
            message.chat.id,
            data
        )

        state = user_data[message.chat.id]

        state["buttons"] = {
            action["text"]: action["id"]
            for action in data.get("actions", [])
        }

        state["gallery_actions"] = {
            action["id"]: action
            for action in data.get("actions", [])
        }

        user_data[message.chat.id] = state

        print(
            "GALLERY BUTTONS:",
            state["buttons"]
        )

        print(
            "GALLERY ACTIONS:",
            state["gallery_actions"]
        )

        return
    # ========================================
    # GALLERY FILE ACTION
    # ========================================

    gallery_actions = user_data.get(
        message.chat.id,
        {}
    ).get(
        "gallery_actions",
        {}
    )

    action = gallery_actions.get(btn_id)

    if action and action.get("type") == "file":

        print("📄 GALLERY FILE ACTION")
        print("FILE ID:", btn_id)
        print("ACTION:", action)

        file_url = action.get("file_url")

        if not file_url:

            print(
                "🔴 GALLERY FILE URL NOT FOUND:",
                btn_id
            )

            return

        file_name = action.get(
            "display_name",
            f"{btn_id}.pdf"
        )

        if file_name.lower().endswith(".pdf"):

            file_type = "document"

        else:

            file_type = "image"

        data = {

            "session_id": str(
                message.chat.id
            ),

            "source_bot": bot_config["bot"],

            "channel": "telegram",

            "chat_id": str(
               message.chat.id
            ),

            "file_name": file_name,

            "file_type": file_type,

            "file_url": file_url,

            "cloudinary_public_id": action.get("public_id"),

            "file_source": "gallery",

            "status": "new"
        }

        response = requests.post(

            f"{SUPABASE_URL}/rest/v1/file_events",

            headers={

                "apikey": SUPABASE_KEY,

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
            print("📤 GALLERY FILE EVENT CREATED")
            print("FILE:", file_name)
            print("TYPE:", file_type)
            print("URL:", file_url)

        else:

            print(
                "🔴 GALLERY FILE EVENT ERROR:",
                response.status_code,
                response.text
            )

        return
    print("🔎 GET PAGE:", repr(btn_id))

    data = get_page(btn_id)
    print("📄 PAGE DATA:", data)
    
    if not data:
        return

    engine = data.get("engine", "page")

    if engine == "popup":

        show_popup(
            message.chat.id,
            data
        )

        return

    elif engine == "calendar":

        data = get_calendar(config=data)

    show_page(
        message.chat.id,
        data
    )


def check_file_messages():

    global file_last_id

    while True:

        try:

            response = requests.get(

                f"{SUPABASE_URL}/rest/v1/{FILE_MESSAGES_TABLE}",

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
                    "FILE MESSAGE ERROR:",
                    response.status_code,
                    response.text
                )

                time.sleep(2)
                continue

            rows = response.json()

            for row in rows:

                file_last_id = row["id"]

                print()
                print("📥 FILE MESSAGE FOR BOT")
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
                        "⚠️ NO CHAT_ID"
                    )

                    continue

                asset_response = requests.get(

                    f"{SUPABASE_URL}/rest/v1/assets",

                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}"
                    },

                    params={
                        "select": "*",
                        "asset_id": f"eq.{row['asset_id']}",
                        "limit": 1
                    },

                    timeout=10
                )

                if asset_response.status_code != 200:

                    print(
                        "ASSET ERROR:",
                        asset_response.status_code
                    )

                    continue

                assets = asset_response.json()

                if not assets:

                    print(
                        "⚠️ ASSET NOT FOUND"
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

                    file_response = requests.get(
                        asset["cloudinary_url"],
                        timeout=30
                    )

                    file_response.raise_for_status()

                    file_data = BytesIO(
                        file_response.content
                    )

                    file_data.name = asset["file_name"]

                    bot.send_document(
                        chat_id,
                        file_data
                    )

                    requests.patch(

                        f"{SUPABASE_URL}/rest/v1/{FILE_MESSAGES_TABLE}",

                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}",
                            "Content-Type": "application/json"
                        },

                        params={
                            "id": f"eq.{row['id']}"
                        },

                        json={
                            "status": "sent",
                            "processed_at": datetime.utcnow().isoformat()
                        },

                        timeout=10
                    )

                    print(
                        "✅ FILE SENT TO USER"
                    )

                except Exception as e:

                    print(
                        "🔴 SEND FILE ERROR:",
                        e
                    )

                    requests.patch(

                        f"{SUPABASE_URL}/rest/v1/{FILE_MESSAGES_TABLE}",

                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}",
                            "Content-Type": "application/json"
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
                "🔴 FILE MESSAGE WORKER ERROR:",
                e
            )

        time.sleep(1)
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
        print("🟢 Lead Bot 1 Running...")
        bot.infinity_polling(
            skip_pending=True,
            timeout=20,
            long_polling_timeout=20
        )

    except Exception as e:

        print("🔴 ERROR:", e)

        time.sleep(5)


