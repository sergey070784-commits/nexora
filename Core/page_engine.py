import requests

PAGES_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/Pages/pages.json"
)


def get_page(page_id):

    pages = requests.get(
        PAGES_URL,
        timeout=10
    ).json()

    page_file = pages.get(page_id)

    if not page_file:
        return None

    return requests.get(
        "https://raw.githubusercontent.com/"
        "sergey070784-commits/nexora/main/Pages/"
        + page_file,
        timeout=10
    ).json()