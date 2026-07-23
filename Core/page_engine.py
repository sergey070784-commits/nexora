import requests

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

entry_points = requests.get(
    BASE + "navigation/entry_points.json",
    timeout=10
).json()

routes = requests.get(
    BASE + "navigation/routes.json",
    timeout=10
).json()

pages = requests.get(
    BASE + "navigation/pages.json",
    timeout=10
).json()


def get_page(key):

    print("KEY:", key)

    page_id = entry_points.get(key)

    if not page_id:
        page_id = routes.get(key)

    print("PAGE_ID:", page_id)

    if not page_id:
        return None

    page_file = pages.get(page_id)

    print("PAGE_FILE:", page_file)

    if not page_file:
        return None

    return requests.get(
        BASE + "pages/" + page_file,
        timeout=10
    ).json()