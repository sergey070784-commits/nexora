import re
import requests

with open("bots/lead-demo.py", encoding="utf-8") as f:
    source = f.read()

match = re.search(r'TOKEN\s*=\s*["\']([^"\']+)["\']', source)

if not match:
    print("TOKEN NOT FOUND")
    raise SystemExit

token = match.group(1)

response = requests.get(
    f"https://api.telegram.org/bot{token}/getWebhookInfo",
    timeout=10
)

print(response.json())