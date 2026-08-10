import requests


LIBRARY_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Service/gallery_library.json"
)


gallery_library = {}


def load_library():

    global gallery_library

    if gallery_library:
        return

    response = requests.get(
        LIBRARY_URL,
        timeout=10
    )

    if response.status_code != 200:
        return

    gallery_library = response.json()


def get_gallery_folder(gallery_id):

    load_library()

    return gallery_library.get(gallery_id)


if __name__ == "__main__":

    print(
        get_gallery_folder("GALLERY_001")
    )