import os
import json
from config import Config

CARE_CONTACTS_FILE = Config.CARE_CONTACTS_FILE
MEDICATIONS_FILE = Config.MEDICATIONS_FILE
FAMILY_CONTACTS_FILE = Config.FAMILY_CONTACTS_FILE
USER_ACTIVITY_FILE = Config.USER_ACTIVITY_FILE

# Utility functions

def load_care_contacts():
    if os.path.exists(CARE_CONTACTS_FILE):
        try:
            with open(CARE_CONTACTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def load_user_medications():
    if os.path.exists(MEDICATIONS_FILE):
        try:
            with open(MEDICATIONS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_user_medications(medications):
    try:
        with open(MEDICATIONS_FILE, "w") as f:
            json.dump(medications, f, indent=2)
    except Exception:
        pass

def load_family_contacts():
    if os.path.exists(FAMILY_CONTACTS_FILE):
        try:
            with open(FAMILY_CONTACTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_family_contacts(contacts):
    try:
        with open(FAMILY_CONTACTS_FILE, "w") as f:
            json.dump(contacts, f, indent=2)
    except Exception:
        pass

def load_user_activity():
    if os.path.exists(USER_ACTIVITY_FILE):
        try:
            with open(USER_ACTIVITY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_user_activity(activity_data):
    try:
        with open(USER_ACTIVITY_FILE, "w") as f:
            json.dump(activity_data, f, indent=2)
    except Exception:
        pass

def update_user_activity(user_id):
    activity_data = load_user_activity()
    import datetime
    activity_data[user_id] = datetime.datetime.now().isoformat()
    save_user_activity(activity_data)
