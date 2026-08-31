import requests

from Core.event_logger import send_event


BTN_DICTIONARY_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "pages/pickers/dictionary/btn_dictionary.json"
)


_order_cache = None


def load_order_map():

    global _order_cache

    if _order_cache is not None:
        return _order_cache

    try:

        response = requests.get(
            BTN_DICTIONARY_URL,
            timeout=10
        )

        response.raise_for_status()

        dictionary = response.json()

        order_map = {}

        for btn_id, data in dictionary.items():

            if not isinstance(data, dict):
                continue

            field = data.get("field")
            value = data.get("value")
            order = data.get("order")

            if not field or not value:
                continue

            if order is None:
                continue

            try:
                order = int(order)
            except (TypeError, ValueError):
                continue

            order_map[
                (str(field), str(value))
            ] = order

        _order_cache = order_map

        print(
            "🧭 VALUE ORDER LOADED:",
            len(order_map)
        )

        return _order_cache

    except Exception as e:

        print(
            "⚠️ VALUE ORDER LOAD ERROR:",
            e
        )

        _order_cache = {}

        return _order_cache


def send_values(

    bot_config,

    chat_id,

    values

):

    if not values:
        return

    order_map = load_order_map()

    indexed_values = list(
        enumerate(values.items())
    )

    def sort_key(item):

        index, (key, value) = item

        order = order_map.get(
            (
                str(key),
                str(value)
            )
        )

        if order is None:
            return (
                1,
                index
            )

        return (
            0,
            order,
            index
        )

    indexed_values.sort(
        key=sort_key
    )

    for _, (key, value) in indexed_values:

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

    user_data.setdefault(
        chat_id,
        {}
    )

    user_data[chat_id]["values"] = values


def get_values(

    user_data,

    chat_id

):

    state = user_data.get(
        chat_id
    )

    if not state:
        return None

    return state.pop(
        "values",
        None
    )