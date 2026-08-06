from Core.event_logger import send_event


def send_values(

    bot_config,

    chat_id,

    values

):

    if not values:
        return

    for key, value in values.items():

        send_event(

            bot_config,

            chat_id,

            value=f"{key}={value}"

        )


def save_values(

    user_data,

    chat_id,

    values

):

    if not values:
        return

    user_data.setdefault(chat_id, {})

    user_data[chat_id]["values"] = values


def get_values(

    user_data,

    chat_id

):

    state = user_data.get(chat_id)

    if not state:
        return None

    return state.pop("values", None)