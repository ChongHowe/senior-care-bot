from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot_utils import load_user_medications, save_user_medications

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})
    if not user_meds:
        await update.message.reply_text("📋 You don't have any medications scheduled yet. Use /medications to add some!")
        return

    for med_key, med in user_meds.items():
        times = ', '.join(med.get('times', []))
        remind_status = med.get('remind', True)
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data=f"remind_yes_{med_key}"),
                InlineKeyboardButton("No", callback_data=f"remind_no_{med_key}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"💊 {med['name']} ({times})\nRemind you for this medication? (Current: {'Yes' if remind_status else 'No'})",
            reply_markup=reply_markup
        )

async def remind_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})
    data = query.data

    if data.startswith("remind_yes_") or data.startswith("remind_no_"):
        med_key = data.split("_", 2)[2]
        remind_value = data.startswith("remind_yes_")
        if med_key in user_meds:
            user_meds[med_key]['remind'] = remind_value
            meds[user_id] = user_meds
            save_user_medications(meds)
            await query.answer()
            await query.edit_message_text(
                f"Reminders for {user_meds[med_key]['name']} set to {'ON' if remind_value else 'OFF'}."
            )
        else:
            await query.answer()
            await query.edit_message_text("Medication not found.")