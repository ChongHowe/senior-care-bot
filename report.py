from telegram import Update
from telegram.ext import ContextTypes
from reporting import generate_weekly_report

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    # You would load medications and medication_log from your data store
    medications = {}      # Replace with real data
    medication_log = []   # Replace with real data

    report_data = generate_weekly_report(user_id, medications, medication_log)
    msg = (
        f"Here is your weekly report:\n"
        f"Taken: {report_data['taken']}\n"
        f"Missed: {report_data['missed']}\n"
        f"Adherence Rate: {report_data['adherence_rate']*100:.1f}%"
    )
    await update.message.reply_text(msg)