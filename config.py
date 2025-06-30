import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = "nigger"
    FLASK_PORT = 5000
    FLASK_HOST = "0.0.0.0"
    
    # Pagination settings
    AIRDROPS_PER_PAGE = 5
    
    # File paths
    DATA_DIR = "data"
    ALLDROPS_FILE = os.path.join(DATA_DIR, "alldrops.json")
    BANNERS_DIR = os.path.join(DATA_DIR, "AirdropBanners")
    USER_DROPS_DIR = os.path.join(DATA_DIR, "UserDrops")
    REMINDERS_DIR = os.path.join(DATA_DIR, "Reminders")
    
    # Reminder options (in minutes)
    REMINDER_OPTIONS = {
        "15 minutes": 15,
        "1 hour": 60,
        "6 hours": 360,
        "1 day": 1440,
        "3 days": 4320,
        "1 week": 10080
    }
