import requests


WORKER_URL = "https://message.sergey070784.workers.dev"


def send_user_text(
    session_id,
    message_text
):

    payload = {
        "session_id": str(session_id),
        "message_text": message_text
    }

    requests.post(
        WORKER_URL,
        json=payload,
        timeout=10
    )