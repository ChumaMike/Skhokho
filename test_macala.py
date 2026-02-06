import requests
import base64
import os

# 1. SETUP: Pick an image you have in the folder (or upload one)
# Replace 'test_image.png' with the name of a real picture on your laptop!
IMAGE_FILENAME = "test_image.png" 

# Check if image exists
if not os.path.exists(IMAGE_FILENAME):
    print(f"❌ Error: Put an image named '{IMAGE_FILENAME}' in this folder first!")
    exit()

# 2. ENCODE: Convert image to Base64 (This is what the Mobile App does)
with open(IMAGE_FILENAME, "rb") as img_file:
    base64_string = base64.b64encode(img_file.read()).decode('utf-8')

# 3. SEND: Talk to Skhokho API
url = "http://localhost:5000/api/v1/ask"
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": "macalaa_super_secret_key_2026"
}
payload = {
    "message": "I am blind. Describe this scene. Is it safe to walk?",
    "image_base64": base64_string
}

print("📡 Sending image to Skhokho Brain...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print("\n✅ SKHOKHO REPLIED:")
    print(response.json()['reply'])
except Exception as e:
    print(f"❌ Failed: {e}")