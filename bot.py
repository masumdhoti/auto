# bot.py
import telebot
from config import BOT_TOKEN, ADMIN_ID
from signup import start_signup
from token_generator import generate_token
from threading import Lock
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}
user_data_lock = Lock()

def check_admin(message):
    """Check if the user is authorized."""
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "🚫 Unauthorized access.")
        return False
    return True

@bot.message_handler(commands=['start'])
def welcome(message):
    if not check_admin(message):
        return
    bot.reply_to(message, "👋 Welcome!\nSend `/gmail yourmail@gmail.com` to begin GitHub account creation.")

@bot.message_handler(commands=['gmail'])
def handle_gmail(message):
    if not check_admin(message):
        return
    try:
        parts = message.text.split()
        if len(parts) != 2 or '@' not in parts[1]:
            logger.warning(f"Invalid gmail command from {message.chat.id}: {message.text}")
            return bot.reply_to(message, "⚠️ Usage: `/gmail yourmail@gmail.com`")
        
        email = parts[1]
        user_id = message.chat.id
        bot.send_message(user_id, f"⏳ Starting GitHub signup for {email}...")
        logger.info(f"Starting signup for {email} by user {user_id}")

        username, password, signup_url = start_signup(email)

        with user_data_lock:
            user_data[user_id] = {
                "email": email,
                "username": username,
                "password": password
            }

        bot.send_message(user_id, f"🔐 Captcha needed. Solve manually:\n👉 {signup_url}\n\nThen send `/otp <code>`")
        logger.info(f"Signup URL sent to user {user_id}: {signup_url}")

    except Exception as e:
        logger.error(f"Error in handle_gmail for {email}: {str(e)}")
        bot.send_message(message.chat.id, f"❌ Error during signup: {str(e)}")

@bot.message_handler(commands=['otp'])
def handle_otp(message):
    if not check_admin(message):
        return
    user_id = message.chat.id
    with user_data_lock:
        if user_id not in user_data:
            logger.warning(f"No user data found for {user_id}")
            return bot.reply_to(message, "⚠️ First send `/gmail yourmail@gmail.com`")

    try:
        parts = message.text.split()
        if len(parts) != 2:
            logger.warning(f"Invalid otp command from {user_id}: {message.text}")
            return bot.reply_to(message, "⚠️ Usage: `/otp <code>`")
        otp = parts[1]
        
        bot.send_message(user_id, f"✅ OTP received: {otp}\nFinishing signup...")
        logger.info(f"Processing OTP for user {user_id}: {otp}")

        with user_data_lock:
            credentials = user_data[user_id]
        token = generate_token(credentials['username'], credentials['password'], otp)

        bot.send_message(user_id, "🎉 Account created!\n\n🧑‍💻 *GitHub Account Info:*\n"
                                  f"`Username:` {credentials['username']}\n"
                                  f"`Password:` {credentials['password']}\n"
                                  f"`Token:` `{token}`", parse_mode='Markdown')
        logger.info(f"Account created for {credentials['email']} (user {user_id})")

        # Clean up user data
        with user_data_lock:
            del user_data[user_id]

    except Exception as e:
        logger.error(f"Error in handle_otp for {user_id}: {str(e)}")
        bot.send_message(user_id, f"❌ Error during OTP processing: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting bot...")
    bot.infinity_polling()