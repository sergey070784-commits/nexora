import os

from Core.cloudinary_gallery import get_gallery_assets


def show_gallery_wa(
    chat_id,
    data
):

    print()
    print("🖼 WA SHOW GALLERY")

    if not data:

        print(
            "🔴 WA GALLERY DATA EMPTY"
        )

        return None

    gallery_id = data.get(
        "gallery_id"
    )

    print(
        "GALLERY ID:",
        gallery_id
    )

    # ========================================
    # LOAD GALLERY ASSETS
    # ========================================

    if gallery_id:

        data["items"] = get_gallery_assets(
            gallery_id
        )

        print(
            "🖼 WA GALLERY ITEMS:",
            len(data["items"])
        )

        for item in data["items"]:

            print(
                "ASSET:",
                item
            )

    # ========================================
    # MATCH FILE ACTIONS
    # ========================================

    assets_by_id = {}

    for item in data.get(
        "items",
        []
    ):

        display_name = item.get(
            "display_name"
        )

        if not display_name:
            continue

        asset_id = os.path.splitext(
            display_name
        )[0]

        assets_by_id[asset_id] = item

    print(
        "🖼 WA CLOUDINARY ASSETS:",
        list(
            assets_by_id.keys()
        )
    )

    for action in data.get(
        "actions",
        []
    ):

        if action.get("type") != "file":
            continue

        asset_id = action.get(
            "id"
        )

        asset = assets_by_id.get(
            asset_id
        )

        if not asset:

            print(
                "🔴 WA FILE ASSET NOT FOUND:",
                asset_id
            )

            continue

        action["file_url"] = asset.get(
            "url"
        )

        action["file_type"] = asset.get(
            "type",
            "document"
        )

        action["public_id"] = asset.get(
            "public_id"
        )

        print()
        print(
            "📎 WA FILE ACTION MATCHED:",
            asset_id
        )

        print(
            "URL:",
            action["file_url"]
        )

    # ========================================
    # PREPARE GALLERY ITEMS
    # ========================================

    gallery_items = []

    for item in data.get(
        "items",
        []
    ):

        item_type = item.get(
            "type"
        )

        url = item.get(
            "url"
        )

        if not url:
            continue

        gallery_items.append({

            "type": item_type,

            "url": url,

            "display_name":
                item.get(
                    "display_name"
                ),

            "public_id":
                item.get(
                    "public_id"
                )

        })

    # ========================================
    # PREPARE ACTIONS
    # ========================================

    actions = data.get(
        "actions",
        []
    )

    gallery_actions = {

        action["id"]: action

        for action in actions

        if action.get("id")

    }

    gallery_buttons = {

        action["text"]:
            action["id"]

        for action in actions

        if action.get("text")
        and action.get("id")

    }

    print()
    print(
        "🖼 WA GALLERY BUTTONS:",
        gallery_buttons
    )

    print(
        "🖼 WA GALLERY ACTIONS:",
        gallery_actions
    )

    # ========================================
    # RETURN WA GALLERY DATA
    # ========================================

    return {

        "id": data.get(
            "id"
        ),

        "gallery_id": gallery_id,

        "items": gallery_items,

        "actions": actions,

        "buttons": gallery_buttons,

        "gallery_actions":
            gallery_actions

    }