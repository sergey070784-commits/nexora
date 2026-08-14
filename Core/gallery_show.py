from telebot import types
from Core.cloudinary_gallery import get_gallery_assets
import os


def show_gallery(bot, chat_id, data):

    print("SHOW GALLERY")

    gallery_id = data.get("gallery_id")

    if gallery_id:

        data["items"] = get_gallery_assets(
            gallery_id
        )
        for item in data["items"]:
            print(
                "ASSET:",
                item
            )

    # ========================================
    # MATCH GALLERY FILE ACTIONS
    # ========================================

    assets_by_id = {}

    for item in data.get("items", []):

        display_name = item.get("display_name")

        if not display_name:
            continue

        asset_id = os.path.splitext(
            display_name
        )[0]

        assets_by_id[asset_id] = item

    print(
        "CLOUDINARY ASSETS:",
        list(assets_by_id.keys())
    )

    for action in data.get("actions", []):

        if action.get("type") != "file":
            continue

        asset_id = action.get("id")

        asset = assets_by_id.get(asset_id)

        if not asset:

            print(
                "🔴 FILE ASSET NOT FOUND:",
                asset_id
            )

            continue

        action["file_url"] = asset.get("url")

        action["file_type"] = asset.get(
            "type",
            "document"
        )

        action["public_id"] = asset.get(
            "public_id"
        )

        print(
            "📎 FILE ACTION MATCHED:",
            asset_id
        )

        print(
            "URL:",
            action["file_url"]
        )

    # ========================================
    # SHOW GALLERY ITEMS
    # ========================================

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

        elif item_type in ("document", "raw"):

            bot.send_document(
                chat_id,
                url
            )

    # ========================================
    # ACTION BUTTONS
    # ========================================

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

    return {
        action["text"]: action["id"]
        for action in actions
    }