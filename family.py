from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot_utils import load_family_contacts, save_family_contacts

async def family(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    family_contacts = load_family_contacts().get(user_id, {})
    msg = "👨‍👩‍👧‍👦 Family Contact Management\n\n"
    keyboard = []

    if not family_contacts:
        msg += "No family contacts set up yet.\nAdd family members to receive important notifications!\n"
    else:
        msg += "Your family contacts:\n"
        for name, info in family_contacts.items():
            msg += f"👤 {info['name']} (ID: {info['id']})\n"
            keyboard.append([
                InlineKeyboardButton(f"Edit {info['name']}", callback_data=f"edit_family_{name}"),
                InlineKeyboardButton(f"Delete {info['name']}", callback_data=f"delete_family_{name}")
            ])
    # Always show the add button
    keyboard.append([InlineKeyboardButton("Add Family Member", callback_data="add_family_member")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msg, reply_markup=reply_markup)

async def family_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    family_contacts = load_family_contacts()
    user_contacts = family_contacts.get(user_id, {})

    if query.data == "add_family_member":
        context.user_data["adding_family"] = True
        context.user_data["editing_family"] = None
        await query.edit_message_text("Please send the family member's name and Telegram user ID in this format:\n\n`Name, TelegramUserID`")
    elif query.data.startswith("edit_family_"):
        name = query.data.replace("edit_family_", "")
        if name in user_contacts:
            context.user_data["editing_family"] = name
            context.user_data["adding_family"] = False
            await query.edit_message_text(
                f"Editing {name}. Please send the new name and Telegram user ID in this format:\n\n`Name, TelegramUserID`"
            )
        else:
            await query.edit_message_text("Family member not found.")
    elif query.data.startswith("delete_family_"):
        name = query.data.replace("delete_family_", "")
        if name in user_contacts:
            del user_contacts[name]
            family_contacts[user_id] = user_contacts
            save_family_contacts(family_contacts)
            await query.edit_message_text(f"Removed family member: {name}")
        else:
            await query.edit_message_text("Family member not found.")

async def family_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    family_contacts = load_family_contacts()
    user_contacts = family_contacts.get(user_id, {})

    # Add new family member
    if context.user_data.get("adding_family"):
        try:
            name, id_str = [x.strip() for x in update.message.text.split(",", 1)]
            user_contacts[name] = {"name": name, "id": int(id_str)}
            family_contacts[user_id] = user_contacts
            save_family_contacts(family_contacts)
            await update.message.reply_text(f"Added family member: {name} (ID: {id_str})")
        except Exception:
            await update.message.reply_text("Invalid format. Please send as: Name, TelegramUserID")
        context.user_data["adding_family"] = False

    # Edit existing family member
    elif context.user_data.get("editing_family"):
        try:
            name, id_str = [x.strip() for x in update.message.text.split(",", 1)]
            old_name = context.user_data["editing_family"]
            # Remove old entry if name changed
            if old_name != name and old_name in user_contacts:
                del user_contacts[old_name]
            user_contacts[name] = {"name": name, "id": int(id_str)}
            family_contacts[user_id] = user_contacts
            save_family_contacts(family_contacts)
            await update.message.reply_text(f"Updated family member: {name} (ID: {id_str})")
        except Exception:
            await update.message.reply_text("Invalid format. Please send as: Name, TelegramUserID")
        context.user_data["editing_family"] = None