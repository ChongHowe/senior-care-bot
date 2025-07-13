import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if TOKEN:
    # Clear any existing webhook
    url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    response = requests.post(url)
    print("Webhook deletion response:", response.json())
    
    # Set to polling mode (no webhook)
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    response = requests.get(url)
    print("Bot info:", response.json())
else:
    print("No BOT_TOKEN found")
