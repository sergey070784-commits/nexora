import requests
import time


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)


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


BOT_CONFIGS = {

    "telegram_bot1":
        "Core/bot1_config.json",

    "telegram_bot2":
        "Core/bot2_config.json",

    "whatsapp_bot1":
        "Core/whatsapp_bot1_config.json",

    "whatsapp_bot2":
        "Core/whatsapp_bot2_config.json"
}


def get_pending_pages():

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/"
        "user_text_page",

        headers=HEADERS,

        params={

            "select": (
                "id,message_id,session_id,"
                "page,status"
            ),

            "status": "eq.pending",

            "order": "id.asc",

            "limit": "20"
        },

        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_message_created_at(message_id):

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/"
        "user_text_messages",

        headers=HEADERS,

        params={

            "select": "created_at",

            "id": f"eq.{message_id}",

            "limit": "1"
        },

        timeout=10
    )

    response.raise_for_status()

    rows = response.json()

    if not rows:
        return None

    return rows[0]["created_at"]


def get_source_event(
    session_id,
    message_created_at
):

    response = requests.get(

        f"{SUPABASE_URL}/rest/v1/"
        "events",

        headers=HEADERS,

        params={

            "select": (
                "id,bot,channel,"
                "value,created_at"
            ),

            "session_id":
                f"eq.{session_id}",

            "created_at":
                f"lte.{message_created_at}",

            "order":
                "created_at.desc",

            "limit": "1"
        },

        timeout=10
    )

    response.raise_for_status()

    rows = response.json()

    if not rows:
        return None

    return rows[0]


def get_bot_config(bot_name):

    path = BOT_CONFIGS.get(
        bot_name
    )

    if not path:
        return None

    response = requests.get(

        BASE + path,

        timeout=10
    )

    response.raise_for_status()

    return response.json()


def update_page(
    page_id,
    source_bot,
    target_bot,
    channel
):

    response = requests.patch(

        f"{SUPABASE_URL}/rest/v1/"
        "user_text_page",

        headers={

            **HEADERS,

            "Content-Type":
                "application/json"
        },

        params={

            "id":
                f"eq.{page_id}"
        },

        json={

            "source_bot":
                source_bot,

            "target_bot":
                target_bot,

            "channel":
                channel,

            "status":
                "new"
        },

        timeout=10
    )

    response.raise_for_status()


def process_page(page):

    page_id = page["id"]

    message_id = page["message_id"]

    session_id = page["session_id"]


    print()

    print(
        "🔎 SPECIALIST 6:",
        message_id
    )

    print(
        "SESSION:",
        session_id
    )


    message_created_at = (
        get_message_created_at(
            message_id
        )
    )


    if not message_created_at:

        raise Exception(
            f"Message time not found: {message_id}"
        )


    source_event = get_source_event(

        session_id,

        message_created_at
    )


    if not source_event:

        raise Exception(
            f"Source event not found: {session_id}"
        )


    source_bot = source_event.get(
        "bot"
    )

    channel = source_event.get(
        "channel"
    )


    print(
        "SOURCE BOT:",
        source_bot
    )

    print(
        "CHANNEL:",
        channel
    )


    if not source_bot:

        raise Exception(
            f"Source bot missing: {message_id}"
        )


    bot_config = get_bot_config(
        source_bot
    )


    if not bot_config:

        raise Exception(
            f"Bot config not found: {source_bot}"
        )


    target_bot = bot_config.get(
        "pair"
    )


    if not target_bot:

        raise Exception(
            f"Pair not found: {source_bot}"
        )


    print(
        "🤝 PARTNER BOT:",
        target_bot
    )


    update_page(

        page_id,

        source_bot,

        target_bot,

        channel
    )


    print(
        "✅ PAGE READY FOR PARTNER:",
        message_id
    )

    print(
        "➡️",
        source_bot,
        "→",
        target_bot
    )


def main():

    print(
        "🧠 USER TEXT SPECIALIST 6 STARTED"
    )


    while True:

        try:

            pages = get_pending_pages()


            for page in pages:

                try:

                    process_page(
                        page
                    )

                except Exception as e:

                    print(
                        "🔴 PAGE ERROR:",
                        page["id"],
                        e
                    )


        except Exception as e:

            print(
                "🔴 SPECIALIST 6 ERROR:",
                e
            )


        time.sleep(2)


if __name__ == "__main__":

    main()