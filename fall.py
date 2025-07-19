from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from bot_utils import load_care_contacts, load_family_contacts

async def fall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("fall() handler called")  # Add this line
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="fall_confirm_yes"),
            InlineKeyboardButton("No", callback_data="fall_confirm_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Have you fallen? Please confirm.",
        reply_markup=reply_markup
    )

async def fall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("fall_callback triggered")  # Debug print
    query = update.callback_query
    user_id = str(query.from_user.id)
    contacts = load_care_contacts()
    user_contacts = contacts.get(user_id, {})
    names = []
    contact_ids = []
    for role, infos in user_contacts.items():
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

    # Load family contacts and add to the list
    family_contacts = load_family_contacts().get(user_id, {})
    for name, info in family_contacts.items():
        if "id" in info:
            names.append(info["name"])
            contact_ids.append(str(info["id"]))

    print(f"Callback data: {update.callback_query.data}")
    print(f"Contact IDs to notify: {contact_ids}")

    if query.data == "fall_confirm_yes":
        print(f"Contact IDs to notify: {contact_ids}")  # Add this line
        # Send alert to contacts
        for contact_id in contact_ids:
            print(f"Trying to send fall alert to contact_id: {contact_id}")
            try:
                await context.bot.send_message(
                    chat_id=contact_id,
                    text=f"🚨 Fall alert! {query.from_user.full_name} may need help."
                )
            except Exception as e:
                print(f"Failed to send fall alert to {contact_id}: {e}")

        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data="fall_send_media_yes"),
                InlineKeyboardButton("No", callback_data="fall_send_media_no")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"✅ Fall alert sent to your contacts: {', '.join(names)}.\n\n"
            "Would you like to send a photo or voice message to help responders?",
            reply_markup=reply_markup
        )
    elif query.data == "fall_confirm_no":
        await query.edit_message_text("Glad you're safe! No alert sent.")
    elif query.data == "fall_send_media_yes":
        context.user_data['fall_waiting_for_media'] = True
        await query.edit_message_text("Please send your photo or voice message now.")
    elif query.data == "fall_send_media_no":
        await query.edit_message_text(
            f"Emergency has been sent to: {', '.join(names)}"
        )

async def fall_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    contacts = load_care_contacts()
    user_contacts = contacts.get(user_id, {})
    names = []
    contact_ids = []
    for role, infos in user_contacts.items():
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

    if context.user_data.get('fall_waiting_for_media'):
        if update.message.photo:
            for contact_id in contact_ids:
                print(f"Trying to send fall photo to contact_id: {contact_id}")  # Debug line
                try:
                    await context.bot.send_photo(
                        chat_id=contact_id,
                        photo=update.message.photo[-1].file_id,
                        caption=f"📷 Photo from {update.effective_user.full_name} (fall alert)"
                    )
                except Exception as e:
                    print(f"Failed to send photo to {contact_id}: {e}")
            await update.message.reply_text(
                f"📷 Photo received.\nEmergency and media have been sent to: {', '.join(names)}"
            )
        elif update.message.voice:
            for contact_id in contact_ids:
                print(f"Trying to send fall voice to contact_id: {contact_id}")  # Debug line
                try:
                    await context.bot.send_voice(
                        chat_id=contact_id,
                        voice=update.message.voice.file_id,
                        caption=f"🎤 Voice message from {update.effective_user.full_name} (fall alert)"
                    )
                except Exception as e:
                    print(f"Failed to send voice message to {contact_id}: {e}")
            await update.message.reply_text(
                f"🎤 Voice message received.\nEmergency and media have been sent to: {', '.join(names)}"
            )
        else:
            await update.message.reply_text("Please send a photo or voice message.")
            return
        context.user_data['fall_waiting_for_media'] = False

def get_emergency_contact_names(user_id):
    contacts = load_care_contacts()
    user_contacts = contacts.get(str(user_id), {})
    names = []
    for role, infos in user_contacts.items():
        if isinstance(infos, list):
            for info in infos:
                if "name" in info:
                    names.append(info["name"])
        elif isinstance(infos, dict) and "name" in infos:
            names.append(infos["name"])
    return names if names else ["No contacts set"]

def get_all_contact_names(user_id):
    names = []
    # Care contacts
    care_contacts = load_care_contacts().get(str(user_id), {})
    for role, infos in care_contacts.items():
        if isinstance(infos, list):
            for info in infos:
                if "name" in info:
                    names.append(info["name"])
        elif isinstance(infos, dict) and "name" in infos:
            names.append(infos["name"])
    # Family contacts
    family_contacts = load_family_contacts().get(str(user_id), {})
    for name, info in family_contacts.items():
        if "name" in info:
            names.append(info["name"])
    return names if names else ["No contacts set"]

async def emergency_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    care_contacts = load_care_contacts().get(user_id, {})
    family_contacts = load_family_contacts().get(user_id, {})
    contact_ids = []

    # Add care contacts
    for role, infos in care_contacts.items():
        if isinstance(infos, dict) and "id" in infos:
            contact_ids.append(str(infos["id"]))
        elif isinstance(infos, list):
            for info in infos:
                if "id" in info:
                    contact_ids.append(str(info["id"]))

    # Add family contacts
    for name, info in family_contacts.items():
        if "id" in info:
            contact_ids.append(str(info["id"]))

    # Remove duplicates
    contact_ids = list(set(contact_ids))

    print(f"Contact IDs for emergency location: {contact_ids}")  # <--- Add this line

    # Send location to all contacts
    for contact_id in contact_ids:
        try:
            await context.bot.send_location(
                chat_id=contact_id,
                latitude=update.message.location.latitude,
                longitude=update.message.location.longitude
            )
        except Exception as e:
            print(f"Failed to send location to {contact_id}: {e}")
    
    await update.message.reply_text(
        f"✅ Your location has been sent to your contacts: {', '.join(get_all_contact_names(user_id))}\n"
        f"Map: https://maps.google.com/maps?q={update.message.location.latitude},{update.message.location.longitude}&ll={update.message.location.latitude},{update.message.location.longitude}&z=16"
    )