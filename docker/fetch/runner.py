import requests, time, os
from datetime import datetime

API = os.environ.get("API_URL")
while (True):
    try:
        res = requests.post(f"{API}/fetch", timeout=120)
        print(f"[{datetime.now().isoformat()}] Status {res.status_code}: {res.text[:200]}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Fetch failed: {e}")
    time.sleep(14400)