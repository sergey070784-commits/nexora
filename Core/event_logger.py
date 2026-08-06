import requests

WORKER_URL = "https://royal-shape-a489.sergey070784.workers.dev"


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

        "message": message,

        "memory": memory

    }

    requests.post(

        WORKER_URL,

        json=payload,

        timeout=10

    )