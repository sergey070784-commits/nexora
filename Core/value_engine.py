import requests

from Core.event_logger import send_event


BTN_DICTIONARY_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "pages/pickers/dictionary/btn_dictionary.json"
)

CONTACT_ROUTES_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Service/contact_routes.json"
)

CONTACT_PAGES_BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Service/contact_viewer/"
)


_order_cache = None


class OrderMap(dict):

    def get(self, key, default=None):

        # ========================================
        # NORMAL BTN LOOKUP
        # (field, value) -> order
        # ========================================

        result = super().get(
            key,
            None
        )

        if result is not None:
            return result

        # ========================================
        # CTN LOOKUP
        # field -> order
        # ========================================

        if (
            isinstance(key, tuple)
            and len(key) == 2
        ):

            field = str(key[0])

            result = super().get(
                ("__FIELD__", field),
                None
            )

            if result is not None:
                return result

        return default


def load_order_map():

    global _order_cache

    if _order_cache is not None:
        return _order_cache

    order_map = OrderMap()

    # ========================================
    # 1. BTN DICTIONARY
    # ========================================

    try:

        response = requests.get(
            BTN_DICTIONARY_URL,
            timeout=10
        )

        response.raise_for_status()

        dictionary = response.json()

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

            except (
                TypeError,
                ValueError
            ):

                continue

            order_map[
                (
                    str(field),
                    str(value)
                )
            ] = order

    except Exception as e:

        print(
            "⚠️ BTN ORDER LOAD ERROR:",
            e
        )


    # ========================================
    # 2. CONTACT ROUTES
    # ========================================

    try:

        response = requests.get(
            CONTACT_ROUTES_URL,
            timeout=10
        )

        response.raise_for_status()

        routes = response.json()

        for ctn_id, page_name in routes.items():

            try:

                page_url = (
                    CONTACT_PAGES_BASE
                    + page_name
                    + ".json"
                )

                page_response = requests.get(
                    page_url,
                    timeout=10
                )

                page_response.raise_for_status()

                data = page_response.json()

                field = data.get("field")
                order = data.get("order")

                if not field:
                    continue

                if order is None:
                    continue

                try:

                    order = int(order)

                except (
                    TypeError,
                    ValueError
                ):

                    continue

                order_map[
                    (
                        "__FIELD__",
                        str(field)
                    )
                ] = order

            except Exception as e:

                print(
                    "⚠️ CTN ORDER ERROR:",
                    ctn_id,
                    e
                )

    except Exception as e:

        print(
            "⚠️ CONTACT ROUTES LOAD ERROR:",
            e
        )


    _order_cache = order_map

    print(
        "🧭 VALUE ORDER LOADED:",
        len(order_map)
    )

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