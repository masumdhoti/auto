# config.py
from dotenv import load_dotenv
import os

load_dotenv()

# Load sensitive data from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
if not ADMIN_ID or not ADMIN_ID.isdigit():
    raise ValueError("ADMIN_ID is not set or invalid in environment variables")

ADMIN_ID = int(ADMIN_ID)