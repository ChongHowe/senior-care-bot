import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    TOKEN = os.getenv("BOT_TOKEN")
    MEDICATIONS_FILE = os.getenv("MEDICATIONS_FILE", "medications.json")
    FAMILY_CONTACTS_FILE = os.getenv("FAMILY_CONTACTS_FILE", "family_contacts.json")
    CARE_CONTACTS_FILE = os.getenv("CARE_CONTACTS_FILE", "care_contacts.json")
    USER_ACTIVITY_FILE = os.getenv("USER_ACTIVITY_FILE", "user_activity.json")
    USER_LOCATIONS_FILE = os.getenv("USER_LOCATIONS_FILE", "user_locations.json")
    MEDICATION_LOG_FILE = os.getenv("MEDICATION_LOG_FILE", "medication_log.txt")
    MISSED_MEDICATION_WINDOW = int(os.getenv("MISSED_MEDICATION_WINDOW", "30"))
    DAILY_CHECKIN_HOURS = int(os.getenv("DAILY_CHECKIN_HOURS", "24"))
