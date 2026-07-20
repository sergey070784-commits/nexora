import telebot
from telebot import types
import requests
from datetime import datetime
import time
import threading
TOKEN = "8826512307:AAG5TzfQEDIC1Q5W8YSiS-GWDI95wucnunY"

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8700197324

user_data = {}

routes = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/navigation/routes.json"
).json()

pages = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/navigation/pages.json"
).json()
popup_routes = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/navigation/popup_routes.json"
).json()

entry_points = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/navigation/entry_points.json"
).json()
bot_config = requests.get(
    "https://raw.githubusercontent.com/sergey070784-commits/nexora/main/Core/bot2_config.json"
).json()
config = requests.get(
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/Core/config.json"
).json()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]
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
    chat_id,
    event,
    value
):

    requests.post(
        "https://royal-shape-a489.sergey070784.workers.dev",
        json={
            "session_id": str(chat_id),

            "timestamp": datetime.now().isoformat(),

            "channel": bot_config["channel"],

            "bot": bot_config["bot"],

            "event": event,

            "value": value
        }
    )
def log_message(chat_id, text):

    try:

        requests.post(

            "https://message.sergey070784.workers.dev/",

            json={

                "session_id": str(chat_id),

                "channel": "telegram",

                "message": text

            },

            timeout=10

        )

    except Exception as e:

        print(e)
def show_page(chat_id, page):

    data = load_page(page)
    track_event(
        chat_id,
        "page_open",
        page
    )
    user_data[chat_id] = {
        "page": page,
        "buttons": {
            button["text"]: button["id"]
            for button in data["buttons"]
        }
    }

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    for button in data["buttons"]:

        keyboard.add(
            types.KeyboardButton(
                button["text"]
            )
        )

    keyboard.add(
        types.KeyboardButton(
            "תפריט"
        )
    )

    text = data["title"]

    for msg in data["messages"]:

        text += "\n\n" + msg

    bot.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )
def show_popup(chat_id, popup):

    data = load_popup(popup)

    user_data[chat_id] = {
        "popup": popup,
        "buttons": {
            button["text"]: button["id"]
            for button in data["buttons"]
        }
    }

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

    if data.get("image"):

        bot.send_photo(
            chat_id,
            data["image"]
        )

    bot.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )
@bot.message_handler(commands=list(entry_points.keys()))
def entry(message):

    command = message.text.split()[0][1:].lower()

    page = entry_points.get(command)

    if page:

        show_page(
            message.chat.id,
            page
        )
@bot.message_handler(commands=['start'])
def start(message):

    parts = message.text.split(maxsplit=1)

    if len(parts) > 1:

        key = parts[1].lower()

        page = entry_points.get(key)

        if page:

            show_page(
                message.chat.id,
                page
            )

            return

    show_page(
        message.chat.id,
        entry_points["lead"]
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):

    current = user_data.get(
        message.chat.id,
        {}
    )

    button_id = (
        current
        .get("buttons", {})
        .get(message.text)
    )

    if button_id:

        track_event(
            message.chat.id,
            "button_click",
            button_id
        )

    else:

        log_message(
            message.chat.id,
            message.text
        )

    if button_id in popup_routes:

        popup = popup_routes[button_id]

        show_popup(
            message.chat.id,
            popup
        )

        return

    if button_id in routes:

        page_id = routes[button_id]

        page = pages[page_id]

        show_page(
            message.chat.id,
            page
        )

        return

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

        print(e)
def command_loop():

    while True:

        check_commands()

        time.sleep(1)
threading.Thread(
    target=command_loop,
    daemon=True
).start()

while True:

    try:
        print("🟢 Lead Bot 2 Running...")
        bot.infinity_polling(
            skip_pending=True,
            timeout=20,
            long_polling_timeout=20
        )

    except Exception as e:

        print("🔴 ERROR:", e)

        time.sleep(5)
