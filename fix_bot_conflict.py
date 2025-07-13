#!/usr/bin/env python3
"""
Fix Telegram Bot Conflict - Singapore Senior Care Bot
Clears webhooks and resets bot to allow polling mode
"""

import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN not found in .env file")
    exit(1)

def clear_webhook():
    """Clear any existing webhook to allow polling"""
    url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    
    print("🔧 Clearing existing webhook...")
    
    try:
        response = requests.post(url)
        result = response.json()
        
        if result.get('ok'):
            print("✅ Webhook cleared successfully!")
            return True
        else:
            print(f"❌ Failed to clear webhook: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing webhook: {str(e)}")
        return False

def get_bot_info():
    """Get bot information to verify token works"""
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            bot_info = result['result']
            print(f"🤖 Bot Info:")
            print(f"   Name: {bot_info.get('first_name', 'N/A')}")
            print(f"   Username: @{bot_info.get('username', 'N/A')}")
            print(f"   ID: {bot_info.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Bot token invalid: {result.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting bot info: {str(e)}")
        return False

def get_webhook_info():
    """Check current webhook status"""
    url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result['result']
            print(f"📡 Webhook Status:")
            print(f"   URL: {webhook_info.get('url', 'None')}")
            print(f"   Pending Updates: {webhook_info.get('pending_update_count', 0)}")
            if webhook_info.get('last_error_date'):
                print(f"   Last Error: {webhook_info.get('last_error_message', 'N/A')}")
            return webhook_info
        else:
            print(f"❌ Could not get webhook info: {result.get('description', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting webhook info: {str(e)}")
        return None

def main():
    print("🇸🇬 SINGAPORE SENIOR CARE BOT - CONFLICT RESOLVER")
    print("=" * 50)
    
    # Step 1: Verify bot token
    print("Step 1: Verifying bot token...")
    if not get_bot_info():
        return
    
    # Step 2: Check webhook status
    print("\nStep 2: Checking webhook status...")
    webhook_info = get_webhook_info()
    
    # Step 3: Clear webhook if exists
    print("\nStep 3: Clearing webhook to enable polling...")
    if clear_webhook():
        print("\n✅ Bot conflict resolved!")
        print("\nYour bot should now work in polling mode.")
        print("You can now run: python bot.py")
    else:
        print("\n❌ Could not resolve conflict.")
        print("Manual steps:")
        print("1. Make sure no other bot instances are running")
        print("2. Check if bot is deployed elsewhere (Heroku, VPS, etc.)")
        print("3. Contact @BotFather if issue persists")

if __name__ == "__main__":
    main()
