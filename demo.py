import os
import django
import requests
import websocket
import threading
import random
import datetime
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlencode

# ----------------------------
# Django setup
# ----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_handler.settings")
django.setup()

# ----------------------------
# Config
# ----------------------------
PAYLOAD_COUNT = 2000
MAX_WORKERS = 4
CHUNK_SIZE = 500

UPLOAD_URL = "http://127.0.0.1:8000/api/data/upload/"
LOGIN_URL = "http://127.0.0.1:8000/admin/login/?next=/admin/"
WS_URL = "ws://127.0.0.1:8000/ws/root/"

USERNAME = "parsa"
PASSWORD = "admin"

# ----------------------------
# Admin session login
# ----------------------------
base_session = requests.Session()

# 1️⃣ GET login page → sets csrftoken cookie
base_session.get(LOGIN_URL)

csrf_token = base_session.cookies.get("csrftoken")
if not csrf_token:
    raise RuntimeError("❌ CSRF token not found")

# 2️⃣ POST login
# 2️⃣ POST login
login_resp = base_session.post(
    LOGIN_URL,
    data={
        "username": USERNAME,
        "password": PASSWORD,
        "csrfmiddlewaretoken": csrf_token,
        "next": "/admin/"
    },
    headers={
        "Referer": LOGIN_URL
    },
    allow_redirects=False
)

# ✅ CHECK LOGIN PROPERLY
if "sessionid" not in base_session.cookies:
    raise RuntimeError("❌ Admin login failed (no sessionid cookie)")

print("✅ Admin session authenticated")
csrf_token = base_session.cookies.get("csrftoken")


# ----------------------------
# Generate payloads
# ----------------------------
payloads = []
time_now = timezone.now()
initial_time = time_now

for _ in range(PAYLOAD_COUNT):
    time_now += timezone.timedelta(minutes=1)
    payloads.append({
        "date": time_now.isoformat(),
        "data": random.randint(1, 100)
    })

# ----------------------------
# WebSocket listener (session-aware)
# ----------------------------
def read_websocket():
    ws = websocket.WebSocket()
    cookie = "; ".join(f"{k}={v}" for k, v in base_session.cookies.items())

    ws.connect(
        WS_URL,
        header=[f"Cookie: {cookie}"]
    )

    count = 0
    while count < PAYLOAD_COUNT:
        ws.recv()
        count += 1

    print(f"[WS] Received {count} messages")
    ws.close()

# ----------------------------
# Ultra-fast uploader (thread-safe)
# ----------------------------
def worker(chunk):
    s = requests.Session()
    s.cookies.update(base_session.cookies)
    headers = {
        "X-CSRFToken": csrf_token
    }
    for p in chunk:
        s.post(UPLOAD_URL, json=p,headers=headers)

def fast_upload():
    chunks = [
        payloads[i:i + CHUNK_SIZE]
        for i in range(0, len(payloads), CHUNK_SIZE)
    ]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(worker, chunks)

# ----------------------------
# Run
# ----------------------------
ws_thread = threading.Thread(target=read_websocket, daemon=True)
req_thread = threading.Thread(target=fast_upload)

start = datetime.datetime.now()

ws_thread.start()
req_thread.start()

req_thread.join()
ws_thread.join()

end = datetime.datetime.now()
print(f"⏱ Total time: {end - start}")

# ----------------------------
# Final analyze call
# ----------------------------
params = {
    "start_time": initial_time.isoformat(),
    "end_time": time_now.isoformat(),
}
final_url = f"http://127.0.0.1:8000/api/data/swing-analyze/?{urlencode(params)}"


resp = base_session.get(final_url)
print("Swing Analyzer:", resp.status_code)
