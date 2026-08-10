import requests

from cloudinary import config as cloudinary_config
from cloudinary.api import resources_by_asset_folder


BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)


CONFIG_URL = BASE + "Core/config.json"

LIBRARY_URL = BASE + "Service/gallery_library.json"


CLOUDINARY_GALLERY_BASE = (
    "Nexora/nexora core/nexora-site/"
    "Gallery_library/"
)


def load_cloudinary_config():

    response = requests.get(
        CONFIG_URL,
        timeout=10
    )

    config = response.json()

    cloudinary_config(
        cloud_name=config["cloudinary_cloud"],
        api_key=config["cloudinary_api_key"],
        api_secret=config["cloudinary_api_secret"]
    )


def load_gallery_library():

    response = requests.get(
        LIBRARY_URL,
        timeout=10
    )

    return response.json()


def get_gallery_assets(gallery_id):

    load_cloudinary_config()

    library = load_gallery_library()

    folder = library.get(gallery_id)

    if not folder:
        return []

    cloudinary_folder = (
        CLOUDINARY_GALLERY_BASE + folder
    )

    result = resources_by_asset_folder(
        cloudinary_folder,
        max_results=100
    )

    assets = []

    for asset in result.get("resources", []):

        url = asset.get("secure_url")

        if not url:
            continue

        url = url.replace(
            "/image/upload/",
            "/image/upload/q_auto/f_auto/"
        )

        assets.append({
            "type": asset.get(
                "resource_type",
                "image"
            ),
            "url": url,
            "public_id": asset.get(
                "public_id"
            )
        })

    return assets


if __name__ == "__main__":

    assets = get_gallery_assets(
        "GALLERY_001"
    )

    print("ASSETS:", len(assets))

    for asset in assets:

        print(
            asset["type"],
            asset["url"]
        )