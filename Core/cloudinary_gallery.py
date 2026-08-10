import requests
from cloudinary import config as cloudinary_config
from cloudinary.api import resources


CONFIG_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Core/config.json"
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


def get_gallery_assets(folder):

    load_cloudinary_config()

    result = resources(
        type="upload",
        prefix=folder,
        max_results=100
    )

    return result.get("resources", [])


if __name__ == "__main__":

    assets = get_gallery_assets(
        "Nexora/Gallery_library/upwork_example_calendar"
    )

    for asset in assets:

        print(
            asset["resource_type"],
            asset["secure_url"]
        )