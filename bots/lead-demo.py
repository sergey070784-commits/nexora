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
TOKEN = "8159696699:AAGOVnHtLK6ELCY32ctYxXFoH8qX6EvZbhc"

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8820758323

user_data = {}

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

bot_config = requests.get(
    BASE + "Core/bot1_config.json",
    timeout=10
).json()

def show_page(chat_id, data):

    user_data[chat_id] = {
        "page": data.get("id"),
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

    bot.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )
def show_popup(chat_id, data):

    user_data[chat_id] = {
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

@bot.message_handler(func=lambda message: True)
def handle_message(message):

    state = user_data.get(message.chat.id)

    if not state:
        return

    btn_id = state["buttons"].get(message.text)

    if not btn_id:

        send_event(

            bot_config,

            message.chat.id,

            message=message.text

        )

        return

    send_event(

        bot_config,

        message.chat.id,

        value=btn_id

    )

    data = get_page(btn_id)
    

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

        data = get_calendar()

    show_page(
        message.chat.id,
        data
    )

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


