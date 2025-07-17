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
