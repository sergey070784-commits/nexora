import telebot
from telebot import types
import requests
from datetime import datetime
import time
import threading
from Core.page_engine import get_page
from Core.popup_engine import get_popup
TOKEN = "8826512307:AAG5TzfQEDIC1Q5W8YSiS-GWDI95wucnunY"

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8700197324

user_data = {}

def show_page(chat_id, key):

    data = get_page(key)

    user_data[chat_id] = {
        "page": key,
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

@bot.message_handler(commands=["start"])
def start(message):

    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:
        return

    entry_key = parts[1]

    show_page(
        message.chat.id,
        entry_key
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):

    state = user_data.get(message.chat.id)

    if not state:
        return

    btn_id = state["buttons"].get(message.text)

    if not btn_id:
        return
    popup = get_popup(btn_id)

    if popup:
        show_popup(
            message.chat.id,
            popup
        )
        return

    show_page(
        message.chat.id,
        btn_id
    )
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
