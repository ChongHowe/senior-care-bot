import os
import json
import portalocker
from config import Config

CARE_CONTACTS_FILE = Config.CARE_CONTACTS_FILE
MEDICATIONS_FILE = Config.MEDICATIONS_FILE
FAMILY_CONTACTS_FILE = Config.FAMILY_CONTACTS_FILE
USER_ACTIVITY_FILE = Config.USER_ACTIVITY_FILE

# Utility functions

def load_care_contacts():
    """Load care contacts from JSON with file-locking."""
    try:
        with portalocker.Lock(CARE_CONTACTS_FILE, 'r', timeout=5) as f:
            return json.load(f)
    except Exception:
        return {}

def save_care_contacts(contacts):
    """Save care contacts to JSON with file-locking."""
    with portalocker.Lock(CARE_CONTACTS_FILE, 'w', timeout=5) as f:
        json.dump(contacts, f, indent=2)

def load_user_medications():
    """Load all user medications from JSON with file-locking."""
    try:
        with portalocker.Lock(MEDICATIONS_FILE, 'r', timeout=5) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_medications(data):
    """Save all user medications to JSON with file-locking."""
    with portalocker.Lock(MEDICATIONS_FILE, 'w', timeout=5) as f:
        json.dump(data, f, indent=2)

def load_family_contacts():
    """Load family contacts from JSON with file-locking."""
    try:
        with portalocker.Lock(FAMILY_CONTACTS_FILE, 'r', timeout=5) as f:
            return json.load(f)
    except Exception:
        return {}

def save_family_contacts(contacts):
    """Save family contacts to JSON with file-locking."""
    with portalocker.Lock(FAMILY_CONTACTS_FILE, 'w', timeout=5) as f:
        json.dump(contacts, f, indent=2)

def load_user_activity():
    """Load user activity from JSON with file-locking."""
    try:
        with portalocker.Lock(USER_ACTIVITY_FILE, 'r', timeout=5) as f:
            return json.load(f)
    except Exception:
        return {}

def save_user_activity(activity_data):
    """Save user activity to JSON with file-locking."""
    with portalocker.Lock(USER_ACTIVITY_FILE, 'w', timeout=5) as f:
        json.dump(activity_data, f, indent=2)

def update_user_activity(user_id):
    """Update the last activity timestamp for a user."""
    activity_data = load_user_activity()
    import datetime
    activity_data[user_id] = datetime.datetime.now().isoformat()
    save_user_activity(activity_data)
