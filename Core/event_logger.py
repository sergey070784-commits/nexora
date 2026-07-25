import requests

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

config = requests.get(
    BASE + "Core/config.json",
    timeout=10
).json()

WORKER_URL = config["worker_url"]


def send_event(
    bot_config,
    session_id,
    value=None,
    message=None
):

    payload = {

        "session_id": str(session_id),

        "channel": bot_config["channel"],

        "bot": bot_config["bot"],

        "value": value,

        "message": message

    }

    requests.post(

        WORKER_URL,

        json=payload,

        timeout=10

    )