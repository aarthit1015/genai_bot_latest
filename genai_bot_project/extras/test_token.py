import requests

#  Hardcode your Telegram Bot Token here:
TOKEN = "BOT KEY"

# Safety check
if not TOKEN or TOKEN.strip() == "":
    print("❌ Please paste your Telegram Bot Token into the script.")
    exit()

# Telegram API endpoint
url = f"https://api.telegram.org/bot{TOKEN}/getMe"

try:
    response = requests.get(url, timeout=10)
    data = response.json()

    if data.get("ok"):
        print(" Token is valid!")
        print(f"Bot name: {data['result']['first_name']}")
        print(f"Bot username: @{data['result']['username']}")
        print(f"Bot ID: {data['result']['id']}")
    else:
        print("❌ Token invalid or unauthorized.")
        print("Error details:", data)

except Exception as e:
    print("⚠️ Network or API error:", e)

