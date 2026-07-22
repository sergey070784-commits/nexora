import requests

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

entry_points = requests.get(
    BASE + "navigation/entry_points.json",
    timeout=10
).json()

pages = requests.get(
    BASE + "navigation/pages.json",
    timeout=10
).json()


def get_page(entry_key):

    page_id = entry_points.get(entry_key)

    if not page_id:
        return None

    page_file = pages.get(page_id)

    if not page_file:
        return None

    return requests.get(
        BASE + "Pages/" + page_file,
        timeout=10
    ).json()