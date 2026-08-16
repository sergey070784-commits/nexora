import requests


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

ROUTES_URL = (
    BASE +
    "Service/contact_viewer/contact_routes.json"
)

PAGES_BASE = (
    BASE +
    "Service/contact_viewer/"
)


def get_contact_data(btn_id):

    response = requests.get(
        ROUTES_URL,
        timeout=10
    )

    response.raise_for_status()

    routes = response.json()

    page_name = routes.get(btn_id)

    if not page_name:
        print(
            "🔴 CONTACT ROUTE NOT FOUND:",
            btn_id
        )

        return None

    page_url = (
        PAGES_BASE +
        page_name +
        ".json"
    )

    response = requests.get(
        page_url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    print()
    print("📋 CONTACT PAGE")
    print("CTN:", btn_id)
    print("PAGE:", page_name)
    print("DATA:", data)

    return data


def show_contact(bot, chat_id, data):

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

    bot.send_message(
        chat_id,
        text
    )

    print(
        "📋 CONTACT SHOWN:",
        data.get("id")
    )