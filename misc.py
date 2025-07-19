from telegram import Update
from telegram.ext import ContextTypes
from bot_utils import load_user_medications, load_care_contacts, load_family_contacts
import json
import os

LOCATION_HISTORY_FILE = "location_history.json"

def load_location_history():
    if not os.path.exists(LOCATION_HISTORY_FILE):
        return {}
    with open(LOCATION_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_location_history(data):
    with open(LOCATION_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})
    if not user_meds:
        await update.message.reply_text("You have no medications scheduled.")
        return

    msg = "🗓️ Your Medication Schedule:\n"
    for med in user_meds.values():
        name = med.get("name", "Unknown")
        times = ', '.join(med.get("times", []))
        msg += f"\n• {name}: {times}"
    await update.message.reply_text(msg)

async def emergency_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📍 EMERGENCY LOCATION HELP\n\n"
        "1. Tap the paperclip 📎 or '+' icon in Telegram's message bar.\n"
        "2. Select 'Location' or 'Share Location'.\n"
        "3. Choose 'Send your current location'.\n\n"
        "Your family will be notified immediately with your location.\n\n"
        "If you need further help, reply with /help or contact your care team."
    )
    await update.message.reply_text(msg)
    context.user_data['awaiting_emergency_location'] = True

async def location_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    history = load_location_history()
    user_history = history.get(user_id, [])
    if not user_history:
        await update.message.reply_text("No location history found.")
        return
    msg = "📍 Your recent locations:\n"
    for i, loc in enumerate(user_history[-10:], 1):  # Show last 10 locations
        lat = loc["lat"]
        lon = loc["lon"]
        map_url = f"https://maps.google.com/maps?q={lat},{lon}&ll={lat},{lon}&z=16"
        msg += f"\n{i}. {map_url}"
    await update.message.reply_text(msg)

async def emergency_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("emergency_location_handler triggered")
    if context.user_data.get('awaiting_emergency_location') and update.message.location:
        user_id = str(update.effective_user.id)
        care_contacts = load_care_contacts().get(user_id, {})
        family_contacts = load_family_contacts().get(user_id, {})
        names = []
        contact_ids = []

        # Add care contacts
        for role, infos in care_contacts.items():
            if isinstance(infos, list):
                for info in infos:
                    if "name" in info:
                        names.append(info["name"])
                    if "id" in info:
                        contact_ids.append(str(info["id"]))
            elif isinstance(infos, dict):
                if "name" in infos:
                    names.append(infos["name"])
                if "id" in infos:
                    contact_ids.append(str(infos["id"]))

        # Add family contacts
        for name, info in family_contacts.items():
            if "name" in info:
                names.append(info["name"])
            if "id" in info:
                contact_ids.append(str(info["id"]))

        # Remove duplicates
        contact_ids = list(set(contact_ids))
        names = list(set(names))

        lat = update.message.location.latitude
        lon = update.message.location.longitude
        map_url = f"https://maps.google.com/maps?q={lat},{lon}&ll={lat},{lon}&z=16"

        # Save location to history
        history = load_location_history()
        user_history = history.get(user_id, [])
        user_history.append({"lat": lat, "lon": lon})
        history[user_id] = user_history
        save_location_history(history)

        # Notify contacts directly
        for contact_id in contact_ids:
            try:
                print(f"Trying to send alert to contact_id: {contact_id}")
                await context.bot.send_message(
                    chat_id=contact_id,
                    text=(
                        f"🚨 Emergency! {update.effective_user.full_name} has shared their location:\n"
                        f"{map_url}"
                    )
                )
            except Exception as e:
                print(f"Failed to send message to {contact_id}: {e}")

        await update.message.reply_text(
            f"✅ Your location has been sent to your contacts: {', '.join(names)}\nMap: {map_url}"
        )
        context.user_data['awaiting_emergency_location'] = False

    print(f"User started bot: {update.effective_user.full_name} ({update.effective_user.id})")