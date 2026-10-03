import sys
import requests


# ========================================
# GITHUB
# ========================================

BASE = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
)

SLOT_URL = BASE + "web/template%20core/site-slot.json"
ERROR_URL = BASE + "web/lawyer-template-01/image-error.json"
CONFIG_URL = BASE + "Core/config.json"


# ========================================
# CONFIG
# ========================================

config = requests.get(
    CONFIG_URL,
    timeout=10
).json()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


# ========================================
# INPUT FROM PYTHON 1
# ========================================

if len(sys.argv) < 2:
    print("ERROR: Site URL was not received")
    sys.exit(1)

site_url = sys.argv[1].rstrip("/")

print()
print("========================================")
print("NEXORA SITE ASSET CHECK")
print("SITE URL:", site_url)
print("========================================")


# ========================================
# FIND SLOT
# ========================================

slots = requests.get(
    SLOT_URL,
    timeout=10
).json()

slot = None

for key, value in slots.items():

    if value.get("url", "").rstrip("/") == site_url:
        slot = key
        break

if not slot:
    print("ERROR: Slot not found for URL")
    sys.exit(1)

print("SLOT FOUND:", slot)


# ========================================
# GET SLOT DATA
# ========================================

response = requests.get(
    f"{SUPABASE_URL}/rest/v1/site_data_users",
    headers=HEADERS,
    params={
        "select": "*",
        "slot": f"eq.{slot}",
        "limit": 1
    },
    timeout=10
)

response.raise_for_status()

rows = response.json()

if not rows:
    print("ERROR: Slot record not found")
    sys.exit(1)

row = rows[0]

site_data = row.get("text-site-data") or {}
image = row.get("image") or ""
photo = site_data.get("photo")

session_id = site_data.get("session_id")
source_id = site_data.get("id")

if not session_id or not source_id:
    print("ERROR: session_id or source id missing")
    sys.exit(1)

print("SESSION:", session_id)
print("SOURCE ID:", source_id)


# ========================================
# IMAGE CHECK
# ========================================

if not image and not photo:

    print("SCENARIO 1: NO IMAGE SELECTED")

elif not image and photo:

    print("SCENARIO 2: PHOTO SELECTED, IMAGE MISSING")

    error_data = requests.get(
        ERROR_URL,
        timeout=10
    ).json()

    error_image = error_data["image-error"]["url"]

    update_image = requests.patch(
        f"{SUPABASE_URL}/rest/v1/site_data_users",
        headers={
            **HEADERS,
            "Prefer": "return=minimal"
        },
        params={
            "slot": f"eq.{slot}"
        },
        json={
            "image": error_image
        },
        timeout=10
    )

    update_image.raise_for_status()

    print("ERROR IMAGE SAVED:", error_image)

else:

    print("IMAGE ALREADY EXISTS:", image)


# ========================================
# COMPLETE SOURCE RECORD
# ========================================

complete = requests.patch(
    f"{SUPABASE_URL}/rest/v1/site_data",
    headers={
        **HEADERS,
        "Prefer": "return=minimal"
    },
    params={
        "id": f"eq.{source_id}",
        "status": "eq.pair"
    },
    json={
    "status": site_url
}
    timeout=10
)

complete.raise_for_status()

print("SOURCE STATUS: pair -> done")


# ========================================
# LAYER 1 RELEASE
# ========================================

print("SESSION:", session_id)
print("SITE URL:", site_url)

print("LAYER 1 RELEASE: NOT CONNECTED YET")
print("SITE ASSET CHECK FINISHED")
