import requests

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

popup_routes = requests.get(
    BASE + "navigation/popup_routes.json",
    timeout=10
).json()

pages = requests.get(
    BASE + "navigation/pages.json",
    timeout=10
).json()

def get_popup(key):

    print("KEY:", key)

    popup_id = popup_routes.get(key)
    print("POPUP_ID:", popup_id)

    if not popup_id:
        return None

    popup_file = pages.get(popup_id)
    print("POPUP_FILE:", popup_file)

    if not popup_file:
        return None

    return requests.get(
        BASE + "pages/" + popup_file,
        timeout=10
    ).json()
