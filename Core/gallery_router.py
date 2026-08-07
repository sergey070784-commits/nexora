from Core.gallery_viewer import get_gallery
import requests

ROUTES_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Service/gallery_viewer/gallery_routes.json"
)

gallery_routes = {}


def load_routes():

    global gallery_routes

    if gallery_routes:
        return

    gallery_routes = requests.get(
        ROUTES_URL,
        timeout=10
    ).json()


def get_gallery_data(grl_id):

    load_routes()

    gallery_id = gallery_routes.get(grl_id)

    if not gallery_id:
        return None

    return get_gallery(gallery_id)


if __name__ == "__main__":

    print(
        get_gallery_data("GRL_00405")
    )