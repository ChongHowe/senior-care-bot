print("Starting bot.py...")

from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import logging
from config import Config
import random
from bot_utils import load_user_medications, save_user_medications, load_care_contacts
from report import report
from family import family, family_callback, family_text_handler
from medications import medications, medications_callback, text_router, medication_add_update_flow
from remind import remind, remind_callback
from fall import fall, fall_callback, fall_media_handler
from misc import schedule, emergency_location, location_history, emergency_location_handler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DEMO_MODE = Config.DEMO_MODE
TOKEN = Config.TOKEN

if DEMO_MODE:
    print("[WARNING] DEMO_MODE is enabled. Changes to contacts and schedules will NOT be saved to file.")
    logger.warning("DEMO_MODE is enabled. Changes to contacts and schedules will NOT be saved to file.")

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
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
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Help command.")

async def care(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Care command.")



def main():
    if not TOKEN:
        print("Error: BOT_TOKEN not set in environment.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

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

    # Specific handlers first
    app.add_handler(CallbackQueryHandler(fall_callback, pattern="^(fall_confirm_yes|fall_confirm_no|fall_send_media_yes|fall_send_media_no)$"))
    app.add_handler(CallbackQueryHandler(remind_callback, pattern="^remind_(yes|no)_"))
    app.add_handler(CallbackQueryHandler(family_callback, pattern="^(add_family_member|delete_family_.*)$"))
    app.add_handler(CallbackQueryHandler(medications_callback, pattern="^(add_med|update_med_|delete_med_)"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, family_text_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VOICE, fall_media_handler))
    app.add_handler(MessageHandler(filters.LOCATION, emergency_location_handler))
    

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

print("emergency_location_handler triggered")
