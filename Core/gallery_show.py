from telebot import types


def show_gallery(bot, chat_id, data):

    print("SHOW GALLERY")

    for item in data.get("items", []):

        item_type = item.get("type")
        url = item.get("url")

        if not url:
            continue

        if item_type == "image":

            bot.send_photo(
                chat_id,
                url
            )

        elif item_type == "document":

            bot.send_document(
                chat_id,
                url
            )

    actions = data.get("actions", [])

    if actions:

        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True
        )

        for action in actions:

            keyboard.add(
                types.KeyboardButton(
                    action["text"]
                )
            )

        bot.send_message(
            chat_id,
            "Gallery",
            reply_markup=keyboard
        )