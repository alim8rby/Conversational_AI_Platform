import requests

url = "http://127.0.0.1:5000/transcribe"
with open("sample.wav", "rb") as f:
    files = {"file": f}
    resp = requests.post(url, files=files)

print("Status code:", resp.status_code)
try:
    data = resp.json()
    print("JSON response:", data)
except ValueError:
    print("Response wasn’t JSON. Raw text:\n", resp.text)
