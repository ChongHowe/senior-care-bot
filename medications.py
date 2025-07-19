from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot_utils import load_user_medications, save_user_medications
import random

async def medications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})

    msg = "📋 Your Medications and Schedule:\n"
    keyboard = []
    if not user_meds:
        msg += "\nYou have no medications scheduled."
    else:
        for med_key, med in user_meds.items():
            times = ', '.join(med.get('times', []))
            remind_status = med.get('remind', True)
            msg += f"\n💊 {med['name']} ({times}) [Remind: {'Yes' if remind_status else 'No'}]"
            keyboard.append([
                InlineKeyboardButton(f"Update {med['name']}", callback_data=f"update_med_{med_key}"),
                InlineKeyboardButton(f"Delete {med['name']}", callback_data=f"delete_med_{med_key}")
            ])
    keyboard.append([InlineKeyboardButton("Add Medication", callback_data="add_med")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, reply_markup=reply_markup)

async def medications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})
    data = query.data

    if data == "add_med":
        context.user_data.clear()
        await query.answer()
        await query.edit_message_text("What is the name of your new medication?")
        context.user_data['med_add_step'] = 'name'
        return

    if data.startswith("update_med_"):
        med_key = data.split("update_med_")[1]
        med = user_meds.get(med_key)
        if not med:
            await query.answer()
            await query.edit_message_text("Medication not found.")
            return
        context.user_data['med_key'] = med_key
        context.user_data['med_add_step'] = 'update'
        await query.answer()
        await query.edit_message_text(
            f"Updating {med['name']}.\nEnter new name (or type 'skip' to keep current: {med['name']}):"
        )
        return

    if data.startswith("delete_med_"):
        med_key = data.split("delete_med_")[1]
        if med_key in user_meds:
            del user_meds[med_key]
            meds[user_id] = user_meds
            save_user_medications(meds)
            await query.answer()
            await query.edit_message_text("Medication deleted.")
        else:
            await query.answer()
            await query.edit_message_text("Medication not found.")
        return

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('med_add_step'):
        await medication_add_update_flow(update, context)
    else:
        await update.message.reply_text("Sorry, I didn't understand that. Use /help for commands.")

async def medication_add_update_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    meds = load_user_medications()
    user_meds = meds.get(user_id, {})
    step = context.user_data.get('med_add_step')
    med_key = context.user_data.get('med_key')

    if step == 'name':
        name = update.message.text.strip()
        if not name:
            await update.message.reply_text("Please enter a valid medication name.")
            return
        med_id = str(random.randint(10000, 99999))
        context.user_data['med_key'] = med_id
        user_meds[med_id] = {'name': name}
        context.user_data['med_add_step'] = 'times'
        await update.message.reply_text("Enter reminder times for this medication (comma-separated, e.g. 08:00, 20:00):")
        return

    if step == 'times':
        times = [t.strip() for t in update.message.text.split(",") if t.strip()]
        med_id = context.user_data['med_key']
        user_meds[med_id]['times'] = times
        context.user_data['med_add_step'] = 'remind'
        await update.message.reply_text("Would you like reminders for this medication? (yes/no)")
        return

    if step == 'remind':
        remind = update.message.text.strip().lower() in ['yes', 'y']
        med_id = context.user_data['med_key']
        user_meds[med_id]['remind'] = remind
        meds[user_id] = user_meds
        save_user_medications(meds)
        await update.message.reply_text("Medication added/updated successfully!")
        context.user_data.pop('med_add_step', None)
        context.user_data.pop('med_key', None)
        return

    if step == 'update':
        med_id = med_key
        med = user_meds.get(med_id, {})
        name = update.message.text.strip()
        if name.lower() != 'skip':
            med['name'] = name
        context.user_data['med_add_step'] = 'update_times'
        await update.message.reply_text(
            f"Enter new times (comma-separated) or type 'skip' to keep current: {', '.join(med.get('times', []))}"
        )
        return

    if step == 'update_times':
        med_id = med_key
        med = user_meds.get(med_id, {})
        times_text = update.message.text.strip()
        if times_text.lower() != 'skip':
            med['times'] = [t.strip() for t in times_text.split(",") if t.strip()]
        context.user_data['med_add_step'] = 'update_remind'
        await update.message.reply_text(
            f"Would you like reminders for this medication? (yes/no, or type 'skip' to keep current: {'Yes' if med.get('remind', True) else 'No'})"
        )
        return

    if step == 'update_remind':
        med_id = med_key
        med = user_meds.get(med_id, {})
        remind_text = update.message.text.strip().lower()
        if remind_text not in ['skip', '']:
            med['remind'] = remind_text in ['yes', 'y']
        meds[user_id] = user_meds
        save_user_medications(meds)
        await update.message.reply_text("Medication updated successfully!")
        context.user_data.pop('med_add_step', None)
        context.user_data.pop('med_key', None)
        return