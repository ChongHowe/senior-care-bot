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
