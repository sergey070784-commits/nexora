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
TOKEN = "8826512307:AAG5TzfQEDIC1Q5W8YSiS-GWDI95wucnunY"

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8700197324

user_data = {}

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

bot_config = requests.get(
    BASE + "Core/bot2_config.json",
    timeout=10
).json()

def show_page(chat_id, data):

        state = user_data.get(chat_id, {})

    state["page"] = data.get("id")

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

    bot.send_message(
        chat_id,
        text,
        reply_markup=keyboard
    )
def show_popup(chat_id, data):

    state = user_data.get(chat_id, {})

    state["page"] = data.get("id")

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

        data = get_calendar(config=data)

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
        print("🟢 Lead Bot 2 Running...")
        bot.infinity_polling(
            skip_pending=True,
            timeout=20,
            long_polling_timeout=20
        )

    except Exception as e:

        print("🔴 ERROR:", e)

        time.sleep(5)


