import requests
print("START")

DICTIONARY_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "pages/pickers/dictionary/gallery_dictionary.json"
)

gallery_dictionary = {}


def load_gallery_dictionary():

    global gallery_dictionary

    if gallery_dictionary:
        return
    

    gallery_dictionary = requests.get(
        DICTIONARY_URL,
        timeout=10
    ).json()


def get_gallery(btn):

    load_gallery_dictionary()

    item = gallery_dictionary.get(btn)

    if not item:
        return None

    return {

        "engine": "gallery",

        "folder": item["folder"]

    }
if __name__ == "__main__":

    print("MAIN")

    print(
        get_gallery("BTN_00405")
    )