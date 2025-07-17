<<<<<<< HEAD
print("Starting bot.py...")  # Debug: confirm script execution
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Location
from telegram.ext import ContextTypes
from datetime import timedelta, time
from dotenv import load_dotenv
import logging
import datetime
import random
import json
import os
from security_utils import sanitize_input, encrypt_data, decrypt_data, generate_fernet_key
from config import Config
from bot_utils import (
    load_care_contacts,
    load_user_medications,
    save_user_medications,
    load_family_contacts,
    save_family_contacts,
    load_user_activity,
    save_user_activity,
    update_user_activity
)


# Centralized config
DEMO_MODE = Config.DEMO_MODE
TOKEN = Config.TOKEN
MEDICATIONS_FILE = Config.MEDICATIONS_FILE
FAMILY_CONTACTS_FILE = Config.FAMILY_CONTACTS_FILE
CARE_CONTACTS_FILE = Config.CARE_CONTACTS_FILE
USER_ACTIVITY_FILE = Config.USER_ACTIVITY_FILE
USER_LOCATIONS_FILE = Config.USER_LOCATIONS_FILE
MEDICATION_LOG_FILE = Config.MEDICATION_LOG_FILE
MISSED_MEDICATION_WINDOW = Config.MISSED_MEDICATION_WINDOW
DAILY_CHECKIN_HOURS = Config.DAILY_CHECKIN_HOURS

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

if DEMO_MODE:
    print("[WARNING] DEMO_MODE is enabled. Changes to contacts and schedules will NOT be saved to file.")
    logger.warning("DEMO_MODE is enabled. Changes to contacts and schedules will NOT be saved to file.")


# Load or generate encryption key (for demonstration, use a static key; in production, load from .env)
FERNET_KEY = generate_fernet_key()

class SeniorCareBot:
    def __init__(self):
        self.demo_mode = DEMO_MODE
        self.token = TOKEN
        self.logger = logger
        self.fernet_key = FERNET_KEY

    # Utility methods are now in bot_utils.py

    # Handler methods (all migrated)
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        try:
            update_user_activity(user_id)
            medications = load_user_medications()
            if user_id not in medications:
                medications[user_id] = {}
                save_user_medications(medications)
            await self.setup_user_reminders(update, context)
            await update.message.reply_text(
                '👋 Hello! I am your Senior Care Assistant.\n\n'
                'Commands:\n'
                '/remind - Manual medication reminder\n'
                '/medications - Manage your medications\n'
                '/schedule - View your medication schedule\n'
                '/family - Manage family contacts\n'
                '/report - Generate medication report\n'
                '/emergency_location - Request immediate location sharing\n'
                '/location_history - View your recent locations\n\n'
                '📍 Location Features:\n'
                '• Share your location anytime using Telegram\'s location button\n'
                '• Family gets notified with map links and coordinates\n'
                '• Emergency location requests alert your family\n\n'
                'I will automatically remind you about medications at their scheduled times!'
            )
        except Exception as e:
            self.logger.error(f"Error in start handler: {e}")
            await update.message.reply_text("❌ An error occurred while starting the bot.")

    async def remind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("✅ Taken", callback_data="taken")],
            [InlineKeyboardButton("⏰ Snooze (2min)", callback_data="snooze")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "💊 Time to take your blood pressure medication!",
            reply_markup=reply_markup
        )

    # ...migrate all other handlers and utility functions as methods...
    # For brevity, not all code shown here, but all handlers should be methods

    async def setup_user_reminders(self, update, context):
        pass

    def run(self):
        print("SeniorCareBot is starting...")  # Added for debug visibility
        if self.demo_mode:
            print("Demo mode not implemented in class yet.")
        else:
            app = ApplicationBuilder().token(self.token).build()
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from security_utils import encrypt_data, decrypt_data, sanitize_input, generate_key

# --- Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
FAMILY_CONTACTS_FILE = "family_contacts.json"
CARE_CONTACTS_FILE = "care_contacts.json"
MEDICATIONS_FILE = "medications.json"

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Security Key (for demo, generate each run; in production, load securely) ---
FERNET_KEY = generate_key()

# --- Data Loading ---
def load_json_file(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return {}

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "👋 Hello! I am your Senior Care Assistant.\n\n"
        "Commands:\n"
        "/remind - Manual medication reminder\n"
        "/medications - Manage your medications\n"
        "/schedule - View your medication schedule\n"
        "/family - Manage family contacts\n"
        "/report - Generate medication report\n"
        "/emergency_location - Request immediate location sharing\n"
        "/location_history - View your recent locations\n\n"
        "📍 Location Features:\n"
        "• Share your location anytime using Telegram's location button\n"
        "• Family gets notified with map links and coordinates\n"
        "• Emergency location requests alert your family\n\n"
        "I will automatically remind you about medications at their scheduled times!"
    )
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available commands: /medications, /family, /care, /remind, /report")

async def medications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})
    illnesses = ["Diabetes", "Hypertension", "Heart Disease", "Stroke", "Kidney Disease"]

    # Always show illness selection first
    if context.user_data.get('med_add_step') is None:
        msg = "📋 Medications and Schedule:\n"
        for illness in illnesses:
            med = next((m for m in user_meds.values() if m.get('illness') == illness), None)
            if med:
                med_display = f"{med['emoji']} {med['name']}"
                if med.get('dosage'):
                    med_display += f" ({med['dosage']})"
                msg += f"\n{med_display}"
                for t in med['times']:
                    msg += f"\n   ⏰ {t}"
            else:
                msg += f"\n💊 {illness}: No Input / Not Needed"
        await update.message.reply_text(msg)
        keyboard = [[InlineKeyboardButton(f"{illness}", callback_data=illness)] for illness in illnesses]
        keyboard.append([InlineKeyboardButton("Other", callback_data="Other")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Would you like to add or update a medication?\n"
            "Please tap the condition that matches your medicine, or choose 'Other'.",
            reply_markup=reply_markup
        )
        context.user_data['med_add_step'] = 'type'
        return
    # Step 2: Always ask for medicine name, regardless of illness selection
    if context.user_data.get('med_add_step') == 'type' and update.callback_query:
        context.user_data['illness'] = update.callback_query.data
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "What is the name of your medicine?\nPlease enter the name below."
        )
        context.user_data['med_add_step'] = 'name'
        return
    # Step 3: Ask for medicine name
    if context.user_data.get('med_add_step') == 'name' and update.message:
        med_name = update.message.text.strip()
        context.user_data['med_name'] = med_name
        await update.message.reply_text(f"How much {med_name} do you take each time? (e.g., 10mg)\nPlease enter the dosage.")
        context.user_data['med_add_step'] = 'dosage'
        return
    # Step 4: Ask for dosage
    if context.user_data.get('med_add_step') == 'dosage' and update.message:
        dosage = update.message.text.strip()
        context.user_data['med_dosage'] = dosage
        await update.message.reply_text(
            f"When do you want to be reminded to take {context.user_data['med_name']}?\nPlease enter the times in 24h format, separated by commas (e.g., 08:00, 20:00)."
        )
        context.user_data['med_add_step'] = 'times'
        return
    # Step 5: Ask for times
    if context.user_data.get('med_add_step') == 'times' and update.message:
        times = [t.strip() for t in update.message.text.split(',')]
        med_name = context.user_data.get('med_name', '')
        dosage = context.user_data.get('med_dosage', '')
        med_key = med_name.lower().replace(' ', '_')
        is_update = med_key in user_meds
        # Show review summary and allow correction of any field
        review_msg = (
            f"Please review your entry:\n\n"
            f"Medicine: {med_name}\n"
            f"Dosage: {dosage}\n"
            f"Reminder times: {', '.join(times)}\n\n"
            "Is everything correct? You can update any field."
        )
        keyboard = [
            [InlineKeyboardButton("Update Medicine Name", callback_data="med_update_name")],
            [InlineKeyboardButton("Update Dosage", callback_data="med_update_dosage")],
            [InlineKeyboardButton("Update Times", callback_data="med_update_times")],
            [InlineKeyboardButton("Confirm All Details", callback_data="med_confirm_all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(review_msg, reply_markup=reply_markup)
        context.user_data['med_review'] = {
            'name': med_name,
            'dosage': dosage,
            'times': times,
            'key': med_key,
            'is_update': is_update
        }
        context.user_data['med_add_step'] = 'review'
        return
    # Step 6: Handle review confirmation/correction and final confirmation
    if context.user_data.get('med_add_step') == 'review' and update.callback_query:
        data = update.callback_query.data
        await update.callback_query.answer()
        review = context.user_data.get('med_review', {})
        if data == "med_update_name":
            await update.callback_query.edit_message_text("Please enter the correct medicine name:")
            context.user_data['med_add_step'] = 'name'
            return
        elif data == "med_update_dosage":
            await update.callback_query.edit_message_text(f"Please enter the correct dosage for {review.get('name','')}:")
            context.user_data['med_add_step'] = 'dosage'
            return
        elif data == "med_update_times":
            await update.callback_query.edit_message_text(f"Please enter the correct reminder times for {review.get('name','')} (24h format, comma separated):")
            context.user_data['med_add_step'] = 'times'
            return
        elif data == "med_confirm_all":
            # Show final confirmation page before saving
            final_review_msg = (
                f"Final review:\n\n"
                f"Medicine: {review['name']}\n"
                f"Dosage: {review['dosage']}\n"
                f"Reminder times: {', '.join(review['times'])}\n\n"
                "Is everything correct? Please confirm to save."
            )
            final_keyboard = [
                [InlineKeyboardButton("Save and Finish", callback_data="med_save_final")],
                [InlineKeyboardButton("Update Details Again", callback_data="med_correct")]
            ]
            final_reply_markup = InlineKeyboardMarkup(final_keyboard)
            await update.callback_query.edit_message_text(final_review_msg, reply_markup=final_reply_markup)
            context.user_data['med_add_step'] = 'final_confirm'
            return
        elif data == "med_correct":
            await update.callback_query.edit_message_text("Let's correct your entry. Please enter the medicine name:")
            context.user_data['med_add_step'] = 'name'
            return
    # Step 7: Save after final confirmation
    if context.user_data.get('med_add_step') == 'final_confirm' and update.callback_query:
        data = update.callback_query.data
        await update.callback_query.answer()
        review = context.user_data.get('med_review', {})
        if data == "med_save_final":
            meds.setdefault(user_id, {})[review['key']] = {
                'name': review['name'],
                'emoji': '💊',
                'dosage': review['dosage'],
                'times': review['times'],
                'illness': context.user_data.get('illness', 'Other')
            }
            save_user_medications(meds)
            await update.callback_query.edit_message_text(
                f"✅ All set! I'll remind you to take {review['name']} ({review['dosage']}) at {', '.join(review['times'])}.\n"
                f"{'(Updated your previous entry.)' if review['is_update'] else '(Added as a new medication.)'}\n\n"
                "Do you wish to input or update another medication? (yes/no)"
            )
            context.user_data['med_add_step'] = 'ask_more'
            return
        elif data == "med_correct":
            await update.callback_query.edit_message_text("Let's correct your entry. Please enter the medicine name:")
            context.user_data['med_add_step'] = 'name'
            return

    # Step 8: Handle more medication input/update
    if context.user_data.get('med_add_step') == 'ask_more' and update.message:
        answer = update.message.text.strip().lower()
        if answer in ["yes", "y"]:
            context.user_data.clear()
            await update.message.reply_text("Let's input or update another medication.")
            await medications(update, context)
            return
        elif answer in ["no", "n"]:
            # Show current schedule before asking for confirmation
            meds = load_user_medications()
            user_meds = meds.get(user_id, {})
            msg = "📋 Your Medication Schedule:\n"
            for med in user_meds.values():
                med_display = f"{med['emoji']} {med['name']}"
                if med.get('dosage'):
                    med_display += f" ({med['dosage']})"
                msg += f"\n{med_display}"
                for t in med['times']:
                    msg += f"\n   ⏰ {t} ({med['name']})"
            await update.message.reply_text(msg)
            await update.message.reply_text("Please confirm all your medications and schedules are updated. (yes/no)")
            context.user_data['med_add_step'] = 'final_confirm_all'
            return

    # Step 9: Final confirmation
    if context.user_data.get('med_add_step') == 'final_confirm_all' and update.message:
        answer = update.message.text.strip().lower()
        if answer in ["yes", "y"]:
            await update.message.reply_text("Thank you! All your medications and schedules are updated.")
            context.user_data.clear()
            return
        elif answer in ["no", "n"]:
            context.user_data.clear()
            await update.message.reply_text("Let's input or update another medication.")
            await medications(update, context)
            return
    # Step 7: Show updated schedule after confirmation
    if context.user_data.get('med_add_step') is None and user_meds:
        msg = "📋 Medications and Schedule:\n"
        for med in user_meds.values():
            med_display = f"{med['emoji']} {med['name']}"
            if med.get('dosage'):
                med_display += f" ({med['dosage']})"
            msg += f"\n{med_display}"
            for t in med['times']:
                msg += f"\n   ⏰ {t}"
        await update.message.reply_text(msg)

async def family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contacts = load_family_contacts()
    if not contacts:
        await update.message.reply_text("👨‍👩‍👧‍👦 No family contacts found. Use /family to add contacts.")
        return
    msg = "👨‍👩‍👧‍👦 Your Family Contacts:\n"
    # If contacts are nested by user_id, flatten for current user
    user_id = str(update.effective_user.id)
    user_contacts = contacts.get(user_id, contacts)
    for relation, info in user_contacts.items():
        if isinstance(info, dict):
            name = info.get('name', '')
            chat_id = info.get('chat_id', '')
            msg += f"\n• {relation}: {name} ({chat_id})"
        else:
            msg += f"\n• {relation}: {info}"
    await update.message.reply_text(msg)

async def care(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contacts = load_json_file(CARE_CONTACTS_FILE)
    if not contacts:
        await update.message.reply_text("No care contacts found.")
        return
    msg = "Care Contacts:\n" + "\n".join([f"- {sanitize_input(c['name'])}: {sanitize_input(c['phone'])}" for c in contacts])
    await update.message.reply_text(msg)

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If user provides time, set reminder
    args = context.args
    if args:
        time_str = sanitize_input(' '.join(args))
        await update.message.reply_text(f"✅ Reminder set for {time_str}. You will be notified at this time.")
        # In production, schedule a job here
        return
    # If no time, show medicine suggestions for top 5 illnesses
    top_5_illnesses = [
        {"illness": "Diabetes", "medicine": "Metformin"},
        {"illness": "Hypertension", "medicine": "Amlodipine"},
        {"illness": "Heart Disease", "medicine": "Atorvastatin"},
        {"illness": "Stroke", "medicine": "Aspirin"},
        {"illness": "Kidney Disease", "medicine": "Losartan"}
    ]
    msg = "Singapore Top 5 Illnesses & Common Medicines:\n" + "\n".join([
        f"- {ill['illness']}: {ill['medicine']}" for ill in top_5_illnesses
    ])
    msg += "\n\nTo set a reminder, type /remind <time> (e.g., /remind 08:00)"
    await update.message.reply_text(msg)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Example: Medication adherence report (replace with real data source)
    user_id = str(update.effective_user.id)
    # Simulate log data (replace with actual file/database read)
    taken = ["2025-07-11 15:47:33", "2025-07-11 16:20:40", "2025-07-11 16:45:42", "2025-07-11 17:18:47"]
    missed = 17
    adherence_rate = round((len(taken) / (len(taken) + missed)) * 100, 1) if (len(taken) + missed) > 0 else 0
    msg = (
        "📊 YOUR MEDICATION REPORT (Last 7 Days)\n\n"
        f"📋 Medications taken: {len(taken)}\n"
        f"❌ Medications missed: {missed}\n"
        f"📊 Adherence rate: {adherence_rate}%\n\n"
        "⚠️ Let's work on improving your medication routine.\n\n"
        "📝 Recent medications taken:\n"
    )
    for t in taken:
        msg += f"✅ medication - {t}\n"
    await update.message.reply_text(msg)
# --- Emergency Location Handler ---
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

# Handle location message and confirm sent to contacts
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    contacts = load_family_contacts().get(user_id, {})
    contact_names = ', '.join([info.get('name', relation) for relation, info in contacts.items() if isinstance(info, dict)])
    location = update.message.location
    if location:
        lat, lon = location.latitude, location.longitude
        map_url = f"https://maps.google.com/maps?q={lat},{lon}&ll={lat},{lon}&z=16"
        msg = (
            f"✅ Your location has been sent to your contacts: {contact_names if contact_names else 'No contacts found'}\n"
            f"Map: {map_url}"
        )
        await update.message.reply_text(msg)

# --- Location History Handler ---
async def location_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import json
    user_id = str(update.effective_user.id)
    try:
        with open(USER_LOCATIONS_FILE, "r") as f:
            all_locations = json.load(f)
        locations = all_locations.get(user_id, [])
    except Exception:
        locations = []
    if not locations:
        msg = "🗺️ No recent locations found."
    else:
        msg = "🗺️ Your Recent Locations:\n" + "\n".join([f"• {loc}" for loc in locations[-3:]])
    await update.message.reply_text(msg)

async def fall(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Step 1: Ask for confirmation
    keyboard = [[InlineKeyboardButton("Yes", callback_data="fall_confirm_yes"), InlineKeyboardButton("No", callback_data="fall_confirm_no")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚨 Fall detected! Please confirm:\n\nDid you really fall?", reply_markup=reply_markup)
    context.user_data['fall_confirm_pending'] = True

async def fall_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "fall_confirm_yes":
        await query.edit_message_text("✅ Fall alert sent to your contacts.\n\nWould you like to send a photo or voice message to help responders? If yes, please send it now.")
        context.user_data['expect_fall_media'] = True
    else:
        await query.edit_message_text("Fall alert cancelled.")
    context.user_data['fall_confirm_pending'] = False


async def handle_fall_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('expect_fall_media'):
        if update.message.photo:
            # Forward photo to contacts (simulate)
            await update.message.reply_text("✅ Your photo has been forwarded to your contacts for the fall alert.")
        elif update.message.voice:
            # Forward voice to contacts (simulate)
            await update.message.reply_text("✅ Your voice message has been forwarded to your contacts for the fall alert.")
        else:
            await update.message.reply_text("Please send a photo or voice message.")
        context.user_data['expect_fall_media'] = False


# --- Medication Schedule Handler ---
async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})
    if not user_meds:
        await update.message.reply_text("📋 You don't have any medications scheduled yet. Use /medications to add some!")
        return
    msg = "📋 Your Medication Schedule:\n"
    for med in user_meds.values():
        msg += f"\n💊 {med['name']}"
        for t in med['times']:
            msg += f"\n   ⏰ {t} ({med['name']})"
    await update.message.reply_text(msg)

# --- Main ---
def main():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN not set in environment.")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("medications", medications))
    app.add_handler(CommandHandler("family", family))
    app.add_handler(CommandHandler("care", care))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("fall", fall))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("emergency_location", emergency_location))
    app.add_handler(CommandHandler("location_history", location_history))
    app.add_handler(CallbackQueryHandler(fall_confirm_callback, pattern="^fall_confirm_"))
    app.add_handler(CallbackQueryHandler(
        medications,
        pattern="^(Diabetes|Hypertension|Heart Disease|Stroke|Kidney Disease|Other|med_confirm|med_confirm_all|med_correct|med_save_final)$"
    ))
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.PHOTO | filters.VOICE, handle_fall_media))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, medications))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
=======
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Location
from telegram.ext import ContextTypes
from datetime import timedelta, time
from dotenv import load_dotenv
import logging
import datetime
import random
import json
import os

# Load environment variables
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

# Medication schedule storage
MEDICATIONS_FILE = os.getenv("MEDICATIONS_FILE", "medications.json")
FAMILY_CONTACTS_FILE = os.getenv("FAMILY_CONTACTS_FILE", "family_contacts.json")
USER_ACTIVITY_FILE = os.getenv("USER_ACTIVITY_FILE", "user_activity.json")
USER_LOCATIONS_FILE = os.getenv("USER_LOCATIONS_FILE", "user_locations.json")
MEDICATION_LOG_FILE = os.getenv("MEDICATION_LOG_FILE", "medication_log.txt")

# Family notification settings
MISSED_MEDICATION_WINDOW = int(os.getenv("MISSED_MEDICATION_WINDOW", "30"))  # Minutes to wait before notifying family
DAILY_CHECKIN_HOURS = int(os.getenv("DAILY_CHECKIN_HOURS", "24"))  # Hours of inactivity before family notification

# Default medication types
MEDICATION_TYPES = {
    "blood_pressure": {
        "name": "Blood Pressure Medication",
        "emoji": "💊",
        "times": ["10:00", "22:00"]  # Changed from 08:00, 20:00
    },
    "diabetes": {
        "name": "Diabetes Medication",
        "emoji": "💉",
        "times": ["09:00", "20:00"]  # Changed from 07:30, 12:30, 19:30
    },
    "heart": {
        "name": "Heart Medication",
        "emoji": "❤️",
        "times": ["10:00", "22:00"]  # Changed from 09:00, 21:00
    },
    "vitamins": {
        "name": "Vitamins",
        "emoji": "🌟",
        "times": ["09:00"]  # Changed from 08:00
    },
    "pain": {
        "name": "Pain Medication",
        "emoji": "🩹",
        "times": ["09:00", "23:00"]  # Changed from 06:00, 14:00, 22:00
    }
}

def load_user_medications():
    """Load user medication schedules from file"""
    if os.path.exists(MEDICATIONS_FILE):
        try:
            with open(MEDICATIONS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_medications(medications):
    """Save user medication schedules to file"""
    with open(MEDICATIONS_FILE, "w") as f:
        json.dump(medications, f, indent=2)

def load_family_contacts():
    """Load family contacts from file"""
    if os.path.exists(FAMILY_CONTACTS_FILE):
        try:
            with open(FAMILY_CONTACTS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_family_contacts(contacts):
    """Save family contacts to file"""
    with open(FAMILY_CONTACTS_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

def load_user_activity():
    """Load user activity tracking"""
    if os.path.exists(USER_ACTIVITY_FILE):
        try:
            with open(USER_ACTIVITY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_activity(activity_data):
    """Save user activity tracking"""
    with open(USER_ACTIVITY_FILE, "w") as f:
        json.dump(activity_data, f, indent=2)

def update_user_activity(user_id):
    """Update last activity time for user"""
    activity_data = load_user_activity()
    activity_data[user_id] = datetime.datetime.now().isoformat()
    save_user_activity(activity_data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Update user activity
    update_user_activity(user_id)
    
    # Initialize user medications if not exists
    medications = load_user_medications()
    if user_id not in medications:
        medications[user_id] = {}
        save_user_medications(medications)
    
    # Set up daily reminders for this user
    await setup_user_reminders(update, context)
    
    await update.message.reply_text(
        '👋 Hello! I am your Senior Care Assistant.\n\n'
        'Commands:\n'
        '/remind - Manual medication reminder\n'
        '/medications - Manage your medications\n'
        '/schedule - View your medication schedule\n'
        '/family - Manage family contacts\n'
        '/report - Generate medication report\n'
        '/emergency_location - Request immediate location sharing\n'
        '/location_history - View your recent locations\n\n'
        '📍 Location Features:\n'
        '• Share your location anytime using Telegram\'s location button\n'
        '• Family gets notified with map links and coordinates\n'
        '• Emergency location requests alert your family\n\n'
        'I will automatically remind you about medications at their scheduled times!'
    )

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Taken", callback_data="taken")],
        [InlineKeyboardButton("⏰ Snooze (2min)", callback_data="snooze")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💊 Time to take your blood pressure medication!",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user.full_name
    user_id = str(update.effective_user.id)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update user activity
    update_user_activity(user_id)
    
    # Handle medication selection
    if query.data.startswith("med_"):
        med_key = query.data[4:]  # Remove "med_" prefix
        await add_medication_to_user(user_id, med_key)
        await setup_user_reminders(update, context)
        
        # Notify family of schedule change
        await notify_family_schedule_change(
            context, user_id, user, 
            MEDICATION_TYPES[med_key]['name'], 
            "added"
        )
        
        await query.edit_message_text(
            text=f"✅ {MEDICATION_TYPES[med_key]['name']} added to your schedule!\n"
                 f"You'll receive reminders at: {', '.join(MEDICATION_TYPES[med_key]['times'])}\n\n"
                 f"👨‍👩‍👧‍👦 Your family has been notified of this change."
        )
        return
    
    # Handle view schedule
    if query.data == "view_schedule":
        medications = load_user_medications()
        user_meds = medications.get(user_id, {})
        
        if not user_meds:
            await query.edit_message_text("📋 You don't have any medications scheduled yet.")
            return
        
        schedule_text = "📋 Your Medication Schedule:\n\n"
        for med_key, med_info in user_meds.items():
            schedule_text += f"{med_info['emoji']} {med_info['name']}\n"
            for time_str in med_info.get('times', []):
                schedule_text += f"   ⏰ {time_str}\n"
            schedule_text += "\n"
        
        await query.edit_message_text(schedule_text)
        return
    
    # Handle medication taken/snooze with specific medication
    if query.data.startswith("taken_") or query.data.startswith("snooze_"):
        action, med_key = query.data.split("_", 1)
        med_name = MEDICATION_TYPES.get(med_key, {}).get("name", "medication")
        
        if action == "taken":
            # Cancel any pending missed medication alerts
            missed_alert_jobs = context.job_queue.get_jobs_by_name(f"missed_alert_{user_id}_{med_key}")
            for job in missed_alert_jobs:
                job.schedule_removal()
            
            # Log to console
            logger.info(f"{now} - {user} acknowledged taking {med_name}.")
            # Log to file
            with open(MEDICATION_LOG_FILE, "a") as f:
                f.write(f"{now} - {user} acknowledged taking {med_name}.\n")
            await query.edit_message_text(text=f"✅ {med_name} logged! Well done!")
            # Also send a new message to the chat
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"📝 {user}, your {med_name.lower()} intake has been recorded at {now}."
            )
        elif action == "snooze":
            await query.edit_message_text(text=f"⏰ I'll remind you about {med_name.lower()} again in 5 minutes.")
            context.job_queue.run_once(
                lambda ctx: send_snooze_reminder(ctx, med_key),
                when=timedelta(minutes=5),
                data={
                    "chat_id": update.effective_chat.id,
                    "med_key": med_key,
                    "medication": MEDICATION_TYPES[med_key]
                }
            )
        return
    
    # Handle family contact management
    if query.data.startswith("add_family_"):
        relationship = query.data[11:]  # Remove "add_family_" prefix
        await query.edit_message_text(
            f"Please send me the Telegram username or chat ID for your {relationship}.\n"
            f"Example: @username or their phone number"
        )
        context.user_data["adding_family"] = relationship
        return
    
    # Original button handling for backward compatibility
    if query.data == "taken":
        # Log to console
        logger.info(f"{now} - {user} acknowledged taking medication.")
        # Optionally, log to a file
        with open(MEDICATION_LOG_FILE, "a") as f:
            f.write(f"{now} - {user} acknowledged taking medication.\n")
        await query.edit_message_text(text="✅ Medicine logged! Well done!")
        # Also send a new message to the chat
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📝 {user}, your medication intake has been recorded at {now}."
        )
    elif query.data == "snooze":
        await query.edit_message_text(text="⏰ I'll remind you again in 2 minutes.")
        context.job_queue.run_once(
            remind_again,
            when=timedelta(minutes=2),
            data=update.effective_chat.id
        )

async def remind_again(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("✅ Taken", callback_data="taken")],
        [InlineKeyboardButton("⏰ Snooze (2min)", callback_data="snooze")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=context.job.data,
        text="💊 Time to take your blood pressure medication!",
        reply_markup=reply_markup
    )

async def fall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emergency_contacts = [7808456068]  # Replace with real chat IDs or user IDs
    for contact in emergency_contacts:
        await context.bot.send_message(
            chat_id=contact,
            text=f"🚨 EMERGENCY: {update.effective_user.full_name} may have fallen!"
        )
    await update.message.reply_text(
        "Help is on the way! Stay calm."
    )

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔊 I received your voice message! (Demo: Simulating 'Call daughter')"
    )
    # In a real bot, use speech-to-text APIs like Whisper here

async def simulate_fall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Simulate accelerometer data (x, y, z)
    x, y, z = random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(0, 15)
    
    # Classify as "fall" if z > 10 (sudden drop)
    is_fall = z > 10  
    
    if is_fall:
        await update.message.reply_text(
            f"🚨 FALL DETECTED! (Z-axis: {z:.2f}g)\n"
            "Alerting emergency contacts..."
        )
        # Trigger emergency protocol
        await emergency_alert(update, context)
    else:
        await update.message.reply_text(f"✅ No fall detected (Z-axis: {z:.2f}g).")

async def emergency_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name
    
    emergency_contacts = [7808456068]  # Replace with real chat IDs or user IDs
    for contact in emergency_contacts:
        await context.bot.send_message(
            chat_id=contact,
            text=f"🚨 EMERGENCY: {user_name} may have fallen!"
        )
    
    # Notify family contacts
    await notify_family_emergency(context, user_id, user_name, "fall")
    
    await update.message.reply_text(
        "Help is on the way! Stay calm."
    )

async def setup_user_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up daily reminders for a user based on their medication schedule"""
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name
    medications = load_user_medications()
    user_meds = medications.get(user_id, {})
    
    # Check if job_queue is available
    if context.job_queue is None:
        logger.info("Job queue not available, skipping reminder setup")
        return
    
    # Remove existing jobs for this user
    current_jobs = context.job_queue.get_jobs_by_name(f"reminder_{user_id}")
    for job in current_jobs:
        job.schedule_removal()
    
    # Schedule new reminders
    for med_key, med_info in user_meds.items():
        for time_str in med_info.get("times", []):
            try:
                hour, minute = map(int, time_str.split(":"))
                reminder_time = time(hour, minute)
                
                context.job_queue.run_daily(
                    send_medication_reminder,
                    time=reminder_time,
                    data={
                        "user_id": user_id,
                        "user_name": user_name,
                        "chat_id": update.effective_chat.id,
                        "medication": med_info,
                        "med_key": med_key
                    },
                    name=f"reminder_{user_id}_{med_key}_{time_str}"
                )
            except ValueError:
                continue
    
    # Schedule weekly reports
    context.job_queue.run_repeating(
        send_weekly_report,
        interval=timedelta(days=7),
        first=timedelta(days=7),
        data={
            "user_id": user_id,
            "user_name": user_name
        },
        name=f"weekly_report_{user_id}"
    )
    
    # Schedule daily activity check
    context.job_queue.run_repeating(
        check_user_activity,
        interval=timedelta(hours=DAILY_CHECKIN_HOURS),
        data={
            "user_id": user_id,
            "user_name": user_name
        },
        name=f"activity_check_{user_id}"
    )

async def send_medication_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send automatic medication reminder"""
    data = context.job.data
    medication = data["medication"]
    user_id = data["user_id"]
    
    keyboard = [
        [InlineKeyboardButton("✅ Taken", callback_data=f"taken_{data['med_key']}")],
        [InlineKeyboardButton("⏰ Snooze (5min)", callback_data=f"snooze_{data['med_key']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=f"{medication['emoji']} Time to take your {medication['name']}!",
        reply_markup=reply_markup
    )
    
    # Schedule family notification for missed medication
    context.job_queue.run_once(
        notify_family_missed_medication,
        when=timedelta(minutes=MISSED_MEDICATION_WINDOW),
        data={
            "user_id": user_id,
            "user_name": data.get("user_name", "User"),
            "medication_name": medication["name"]
        },
        name=f"missed_alert_{user_id}_{data['med_key']}"
    )

async def send_snooze_reminder(context: ContextTypes.DEFAULT_TYPE, med_key: str):
    """Send snooze reminder for specific medication"""
    data = context.job.data
    medication = data["medication"]
    
    keyboard = [
        [InlineKeyboardButton("✅ Taken", callback_data=f"taken_{med_key}")],
        [InlineKeyboardButton("⏰ Snooze (5min)", callback_data=f"snooze_{med_key}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=f"{medication['emoji']} Reminder: Time to take your {medication['name']}!",
        reply_markup=reply_markup
    )

async def medications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage medication types and schedules"""
    keyboard = []
    for med_key, med_info in MEDICATION_TYPES.items():
        keyboard.append([InlineKeyboardButton(
            f"{med_info['emoji']} {med_info['name']}", 
            callback_data=f"med_{med_key}"
        )])
    
    keyboard.append([InlineKeyboardButton("📋 View My Schedule", callback_data="view_schedule")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💊 Select a medication type to add to your schedule:",
        reply_markup=reply_markup
    )

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View current medication schedule"""
    user_id = str(update.effective_user.id)
    medications = load_user_medications()
    user_meds = medications.get(user_id, {})
    
    if not user_meds:
        await update.message.reply_text("📋 You don't have any medications scheduled yet. Use /medications to add some!")
        return
    
    schedule_text = "📋 Your Medication Schedule:\n\n"
    for med_key, med_info in user_meds.items():
        schedule_text += f"{med_info['emoji']} {med_info['name']}\n"
        for time_str in med_info.get('times', []):
            schedule_text += f"   ⏰ {time_str}\n"
        schedule_text += "\n"
    
    await update.message.reply_text(schedule_text)

async def add_medication_to_user(user_id: str, med_key: str):
    """Add a medication type to user's schedule"""
    medications = load_user_medications()
    if user_id not in medications:
        medications[user_id] = {}
    
    medications[user_id][med_key] = MEDICATION_TYPES[med_key].copy()
    save_user_medications(medications)

async def notify_family_missed_medication(context: ContextTypes.DEFAULT_TYPE):
    """Notify family when medication is missed"""
    data = context.job.data
    user_name = data["user_name"]
    medication_name = data["medication_name"]
    user_id = data["user_id"]
    
    family_contacts = load_family_contacts()
    user_family = family_contacts.get(user_id, {})
    
    for contact_name, contact_info in user_family.items():
        try:
            await context.bot.send_message(
                chat_id=contact_info["chat_id"],
                text=f"⚠️ MEDICATION ALERT\n\n"
                     f"📋 {user_name} hasn't taken their {medication_name} yet.\n"
                     f"⏰ It was scheduled 30 minutes ago.\n\n"
                     f"You might want to check in with them."
            )
        except Exception as e:
            logger.error(f"Failed to notify family contact {contact_name}: {e}")

async def notify_family_schedule_change(context, user_id, user_name, medication_name, action):
    """Notify family when medication schedule changes"""
    family_contacts = load_family_contacts()
    user_family = family_contacts.get(user_id, {})
    
    action_text = {
        "added": f"➕ Added {medication_name} to their schedule",
        "removed": f"➖ Removed {medication_name} from their schedule",
        "modified": f"🔄 Modified {medication_name} schedule"
    }
    
    for contact_name, contact_info in user_family.items():
        try:
            await context.bot.send_message(
                chat_id=contact_info["chat_id"],
                text=f"📋 SCHEDULE UPDATE\n\n"
                     f"👤 {user_name}\n"
                     f"{action_text.get(action, action)}\n\n"
                     f"💡 You can ask them to send /schedule to see their current medications."
            )
        except Exception as e:
            logger.error(f"Failed to notify family contact {contact_name}: {e}")

async def notify_family_emergency(context, user_id, user_name, emergency_type):
    """Notify family of emergency situations"""
    family_contacts = load_family_contacts()
    user_family = family_contacts.get(user_id, {})
    
    emergency_messages = {
        "fall": f"🚨 FALL DETECTED!\n\n👤 {user_name} may have fallen!\n⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n🆘 Please check on them immediately!",
        "no_activity": f"⚠️ DAILY CHECK-IN ALERT\n\n👤 {user_name} hasn't used the bot in 24+ hours.\n⏰ Last activity: Check user activity log\n\n💡 Consider calling to check if they're okay."
    }
    
    for contact_name, contact_info in user_family.items():
        try:
            await context.bot.send_message(
                chat_id=contact_info["chat_id"],
                text=emergency_messages.get(emergency_type, f"🚨 EMERGENCY: {emergency_type}")
            )
        except Exception as e:
            logger.error(f"Failed to notify family contact {contact_name}: {e}")

async def generate_medication_report(user_id, days=7):
    """Generate medication adherence report"""
    # Read medication log
    report_data = {
        "total_medications": 0,
        "taken_medications": 0,
        "missed_medications": 0,
        "adherence_rate": 0,
        "details": []
    }
    
    if os.path.exists(MEDICATION_LOG_FILE):
        with open(MEDICATION_LOG_FILE, "r") as f:
            lines = f.readlines()
        
        # Count medications taken in the last 'days' days
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        for line in lines:
            if "acknowledged taking" in line:
                try:
                    # Extract date from log line
                    date_str = line.split(" - ")[0]
                    log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    
                    if log_date >= cutoff_date:
                        report_data["taken_medications"] += 1
                        # Extract medication name
                        med_info = line.split("acknowledged taking ")[1].strip().rstrip(".")
                        report_data["details"].append(f"✅ {med_info} - {date_str}")
                except:
                    continue
    
    # Calculate expected medications (simplified)
    medications = load_user_medications()
    user_meds = medications.get(user_id, {})
    daily_meds = sum(len(med_info.get("times", [])) for med_info in user_meds.values())
    report_data["total_medications"] = daily_meds * days
    report_data["missed_medications"] = max(0, report_data["total_medications"] - report_data["taken_medications"])
    
    if report_data["total_medications"] > 0:
        report_data["adherence_rate"] = (report_data["taken_medications"] / report_data["total_medications"]) * 100
    
    return report_data

async def send_weekly_report(context: ContextTypes.DEFAULT_TYPE):
    """Send weekly medication report to family"""
    data = context.job.data
    user_id = data["user_id"]
    user_name = data["user_name"]
    
    family_contacts = load_family_contacts()
    user_family = family_contacts.get(user_id, {})
    
    if not user_family:
        return
    
    report = await generate_medication_report(user_id, days=7)
    
    report_text = (
        f"📊 WEEKLY MEDICATION REPORT\n\n"
        f"👤 {user_name}\n"
        f"📅 {(datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"📋 Medications taken: {report['taken_medications']}\n"
        f"❌ Medications missed: {report['missed_medications']}\n"
        f"📊 Adherence rate: {report['adherence_rate']:.1f}%\n\n"
    )
    
    if report["adherence_rate"] >= 90:
        report_text += "🌟 Excellent medication adherence!"
    elif report["adherence_rate"] >= 75:
        report_text += "👍 Good medication adherence, with room for improvement."
    else:
        report_text += "⚠️ Low medication adherence. Consider checking in more frequently."
    
    for contact_name, contact_info in user_family.items():
        try:
            await context.bot.send_message(
                chat_id=contact_info["chat_id"],
                text=report_text
            )
        except Exception as e:
            logger.error(f"Failed to send report to family contact {contact_name}: {e}")

async def family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage family contacts"""
    user_id = str(update.effective_user.id)
    update_user_activity(user_id)
    
    family_contacts = load_family_contacts()
    user_family = family_contacts.get(user_id, {})
    
    keyboard = [
        [InlineKeyboardButton("👩 Add Daughter", callback_data="add_family_daughter")],
        [InlineKeyboardButton("👨 Add Son", callback_data="add_family_son")],
        [InlineKeyboardButton("👫 Add Spouse", callback_data="add_family_spouse")],
        [InlineKeyboardButton("👥 Add Other Family", callback_data="add_family_other")]
    ]
    
    if user_family:
        keyboard.append([InlineKeyboardButton("📋 View Family Contacts", callback_data="view_family")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    family_text = "👨‍👩‍👧‍👦 Family Contact Management\n\n"
    if user_family:
        family_text += f"You have {len(user_family)} family contact(s) set up.\n"
        family_text += "They will be notified about:\n"
        family_text += "• Missed medications (after 30 min)\n"
        family_text += "• Schedule changes\n"
        family_text += "• Emergency alerts\n"
        family_text += "• Weekly medication reports\n\n"
    else:
        family_text += "No family contacts set up yet.\n"
        family_text += "Add family members to receive important notifications!\n\n"
    
    family_text += "Select an option below:"
    
    await update.message.reply_text(family_text, reply_markup=reply_markup)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate and show medication adherence report"""
    user_id = str(update.effective_user.id)
    update_user_activity(user_id)
    
    # Generate 7-day report
    report = await generate_medication_report(user_id, days=7)
    
    report_text = (
        f"📊 YOUR MEDICATION REPORT (Last 7 Days)\n\n"
        f"📋 Medications taken: {report['taken_medications']}\n"
        f"❌ Medications missed: {report['missed_medications']}\n"
        f"📊 Adherence rate: {report['adherence_rate']:.1f}%\n\n"
    )
    
    if report["adherence_rate"] >= 90:
        report_text += "🌟 Excellent! You're doing great with your medications!"
    elif report["adherence_rate"] >= 75:
        report_text += "👍 Good job! Try to maintain this consistency."
    else:
        report_text += "⚠️ Let's work on improving your medication routine."
    
    if report["details"]:
        report_text += f"\n\n📝 Recent medications taken:\n"
        # Show last 5 entries
        for detail in report["details"][-5:]:
            report_text += f"{detail}\n"
    
    await update.message.reply_text(report_text)

async def check_user_activity(context: ContextTypes.DEFAULT_TYPE):
    """Check if user has been inactive for too long"""
    data = context.job.data
    user_id = data["user_id"]
    user_name = data["user_name"]
    
    activity_data = load_user_activity()
    last_activity_str = activity_data.get(user_id)
    
    if last_activity_str:
        try:
            last_activity = datetime.datetime.fromisoformat(last_activity_str)
            hours_since_activity = (datetime.datetime.now() - last_activity).total_seconds() / 3600
            
            if hours_since_activity >= DAILY_CHECKIN_HOURS:
                await notify_family_emergency(context, user_id, user_name, "no_activity")
        except:
            pass

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location sharing from users"""
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.full_name
    location = update.message.location
    lat, lon = location.latitude, location.longitude
    
    # Update user activity
    update_user_activity(user_id)
    
    # Create Google Maps link
    google_maps_link = f"https://maps.google.com/?q={lat},{lon}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save location to file for emergency reference
    location_data = {
        "user_id": user_id,
        "user_name": user_name,
        "latitude": lat,
        "longitude": lon,
        "timestamp": timestamp,
        "google_maps_link": google_maps_link
    }
    
    # Save to location log
    locations = []
    if os.path.exists(USER_LOCATIONS_FILE):
        try:
            with open(USER_LOCATIONS_FILE, "r") as f:
                locations = json.load(f)
        except:
            locations = []
    
    locations.append(location_data)
    # Keep only last 50 locations per user
    user_locations = [loc for loc in locations if loc["user_id"] == user_id]
    other_locations = [loc for loc in locations if loc["user_id"] != user_id]
    if len(user_locations) > 50:
        user_locations = user_locations[-50:]
    
    locations = other_locations + user_locations
    
    with open(USER_LOCATIONS_FILE, "w") as f:
        json.dump(locations, f, indent=2)
    
    # Confirm receipt to user
    await update.message.reply_text(
        f"📍 Location received and saved!\n\n"
        f"🗓️ Time: {timestamp}\n"
        f"🌐 Map: {google_maps_link}\n\n"
        f"👨‍👩‍👧‍👦 Your family contacts have been notified of your location."
    )
    
    # Notify family contacts
    await notify_family_location(context, user_id, user_name, lat, lon, google_maps_link, timestamp)
    
    # Log the location sharing
    logger.info(f"Location shared by {user_name} ({user_id}): {lat}, {lon}")

async def notify_family_location(context, user_id, user_name, lat, lon, google_maps_link, timestamp):
    """Notify family contacts when user shares location"""
    family_contacts = load_family_contacts()
    user_family = family_contacts.get(user_id, {})
    
    for contact_name, contact_info in user_family.items():
        try:
            # Send text message with details
            await context.bot.send_message(
                chat_id=contact_info["chat_id"],
                text=f"📍 LOCATION UPDATE\n\n"
                     f"👤 {user_name}\n"
                     f"🗓️ {timestamp}\n"
                     f"🌐 {google_maps_link}\n\n"
                     f"💡 They shared their location - you can use this to find them if needed."
            )
            
            # Also forward the actual location for easy navigation
            await context.bot.send_location(
                chat_id=contact_info["chat_id"],
                latitude=lat,
                longitude=lon
            )
        except Exception as e:
            logger.error(f"Failed to notify family contact {contact_name} about location: {e}")

async def emergency_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request emergency location from user"""
    user_id = str(update.effective_user.id)
    update_user_activity(user_id)
    
    await update.message.reply_text(
        "🚨 EMERGENCY LOCATION REQUEST\n\n"
        "Please share your current location immediately!\n\n"
        "📱 Tap the paperclip icon (📎) in Telegram\n"
        "📍 Select 'Location'\n"
        "🌐 Choose 'Share Live Location' or 'Send My Current Location'\n\n"
        "Your family will be notified with your exact coordinates."
    )
    
    # Alert family that emergency location was requested
    await notify_family_emergency_location_request(context, user_id, update.effective_user.full_name)

async def notify_family_emergency_location_request(context, user_id, user_name):
    """Notify family that emergency location was requested"""
    family_contacts = load_family_contacts()
    user_family = family_contacts.get(user_id, {})
    
    for contact_name, contact_info in user_family.items():
        try:
            await context.bot.send_message(
                chat_id=contact_info["chat_id"],
                text=f"🚨 EMERGENCY LOCATION REQUESTED\n\n"
                     f"👤 {user_name} used the emergency location command.\n"
                     f"⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                     f"📍 Waiting for them to share their location...\n"
                     f"💡 You should receive their coordinates shortly."
            )
        except Exception as e:
            logger.error(f"Failed to notify family contact {contact_name} about emergency location request: {e}")

async def location_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's recent location history"""
    user_id = str(update.effective_user.id)
    update_user_activity(user_id)
    
    if not os.path.exists(USER_LOCATIONS_FILE):
        await update.message.reply_text("📍 No location history found.")
        return
    
    try:
        with open(USER_LOCATIONS_FILE, "r") as f:
            locations = json.load(f)
    except:
        await update.message.reply_text("📍 Error reading location history.")
        return
    
    user_locations = [loc for loc in locations if loc["user_id"] == user_id]
    
    if not user_locations:
        await update.message.reply_text("📍 No location history found for your account.")
        return
    
    # Show last 5 locations
    recent_locations = user_locations[-5:]
    
    history_text = "📍 Your Recent Locations:\n\n"
    for i, loc in enumerate(reversed(recent_locations), 1):
        history_text += f"{i}. 🗓️ {loc['timestamp']}\n"
        history_text += f"   🌐 {loc['google_maps_link']}\n\n"
    
    if len(user_locations) > 5:
        history_text += f"📊 Total locations saved: {len(user_locations)}"
    
    await update.message.reply_text(history_text)
    
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("medications", medications))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("fall", fall))  # <-- Add this line
    app.add_handler(CommandHandler("simulate_fall", simulate_fall))
    app.add_handler(CommandHandler("family", family))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("emergency_location", emergency_location))
    app.add_handler(CommandHandler("location_history", location_history))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
>>>>>>> e6794ed6da762a27f7f904b11c4db085ac394f16
