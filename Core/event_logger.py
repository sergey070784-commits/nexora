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

        "message": message


    }

    requests.post(

        WORKER_URL,

        json=payload,

        timeout=10

    )
def send_ctn_event(
    bot_config,
    session_id,
    field,
    text,
    next_id
):
    # Сначала сохраняем введённый текст
    send_event(
        bot_config=bot_config,
        session_id=session_id,
        value=f"{field}={text}"
    )

    # Только после этого регистрируем следующий BTN
    if next_id and next_id.startswith("BTN_"):
        send_event(
            bot_config=bot_config,
            session_id=session_id,
            value=next_id
        )