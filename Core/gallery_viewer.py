import requests

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Service/gallery_viewer/"
)


def get_gallery(gallery_id):

    response = requests.get(
        BASE + f"{gallery_id}.json",
        timeout=10
    )
    
    if response.status_code != 200:
        return None

    return response.json()


if __name__ == "__main__":

    print(
        get_gallery("galli_00001")
    )