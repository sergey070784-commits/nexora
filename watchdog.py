import requests
import time
import subprocess
import sys
from datetime import datetime, timezone


# ========================================
# CONFIG
# ========================================

CONFIG_URL = (
    "https://raw.githubusercontent.com/"
    "sergey070784-commits/nexora/main/"
    "Core/config.json"
)

LOCAL_CONFIG = "Core/config.json"

CHECK_INTERVAL = 6 * 60 * 60       # 6 hours
RECHECK_DELAY = 5 * 60             # 5 minutes
EVENT_SILENCE = 5 * 60             # 5 minutes

RESTART_BAT = r".\restart_21.bat"


# ========================================
# LOAD CONFIG
# ========================================

def load_config():

    try:

        with open(
            LOCAL_CONFIG,
            "r",
            encoding="utf-8"
        ) as f:

            print("📁 CONFIG: local")
            return __import__("json").load(f)

    except Exception:

        print("🌐 CONFIG: GitHub")

        response = requests.get(
            CONFIG_URL,
            timeout=10
        )

        response.raise_for_status()

        return response.json()


config = load_config()

SUPABASE_URL = config["supabase_url"]
SUPABASE_KEY = config["supabase_key"]


HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}


# ========================================
# EVENTS
# ========================================

def get_last_event():

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/events",
        headers=HEADERS,
        params={
            "select": "created_at",
            "order": "created_at.desc",
            "limit": 1
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return data[0]["created_at"]


def check_events():

    last_event = get_last_event()

    if not last_event:

        print("⚠️ EVENTS: no events found")

        return False

    last_dt = datetime.fromisoformat(
        last_event.replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    age = (now - last_dt).total_seconds()

    print(
        f"📡 EVENTS: last event "
        f"{int(age)} seconds ago"
    )

    if age < EVENT_SILENCE:

        print("🟢 EVENTS ACTIVE")

        return True

    print("🟡 EVENTS SILENT")

    return False


# ========================================
# RESTART
# ========================================

def restart_system():

    print()
    print("🔴 WATCHDOG → RESTART 21 PROCESSES")
    print()

    subprocess.Popen(
        [
            "cmd",
            "/c",
            RESTART_BAT
        ],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )


# ========================================
# ONE CHECK
# ========================================

def check_once():

    print()
    print("=" * 55)
    print(
        "🛡️ WATCHDOG CHECK",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )
    print("=" * 55)

    try:

        if check_events():

            print(
                "🟢 SYSTEM ACTIVE → NO RESTART"
            )

            return

        print(
            "🟡 NO RECENT EVENTS"
        )

        print(
            "⏳ WAITING 5 MINUTES..."
        )

        time.sleep(RECHECK_DELAY)

        print()
        print("🔎 SECOND CHECK")

        if check_events():

            print(
                "🟢 EVENTS APPEARED → NO RESTART"
            )

            return

        print(
            "🔴 EVENTS STILL SILENT"
        )

        restart_system()

    except Exception as e:

        print(
            "🔴 WATCHDOG ERROR:",
            e
        )


# ========================================
# MAIN
# ========================================

print()
print("🛡️ NEXORA WATCHDOG STARTED")
print("⏱️ CHECK EVERY 6 HOURS")
print()

# Manual one-time check
if "--once" in sys.argv:

    print("🧪 ONE-TIME CHECK MODE")
    check_once()

    print()
    print("🛑 WATCHDOG FINISHED")
    sys.exit(0)


# Normal watchdog mode
while True:

    check_once()

    print()
    print("💤 NEXT CHECK IN 6 HOURS")
    print()

    time.sleep(CHECK_INTERVAL)