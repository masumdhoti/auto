# signup.py
import random
import string
import re
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def random_username():
    """Generate a random username."""
    return "user" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def random_password():
    """Generate a random password."""
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=12))

def start_signup(email):
    """Start GitHub signup process and return username, password, and CAPTCHA URL."""
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        logger.error(f"Invalid email format: {email}")
        raise ValueError("Invalid email format")

    username = random_username()
    password = random_password()

    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = None  # Initialize driver as None to avoid reference errors
    try:
        logger.info("Initializing Chrome driver...")
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        logger.info(f"Navigating to GitHub signup for {email}")
        driver.get("https://github.com/signup")
        wait = WebDriverWait(driver, 10)

        # Enter email
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys(email)

        # Click continue button
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-optimizely-event='click.signup_continue.email']")))
        button.click()

        # Wait for redirect (CAPTCHA page)
        wait.until(EC.url_contains("signup?"))
        signup_url = driver.current_url
        logger.info(f"Signup URL generated: {signup_url}")

        return username, password, signup_url

    except Exception as e:
        logger.error(f"Error during signup for {email}: {str(e)}")
        if driver:
            try:
                driver.save_screenshot("signup_error.png")  # Save screenshot only if driver exists
            except Exception as screenshot_error:
                logger.warning(f"Failed to save screenshot: {str(screenshot_error)}")
        raise

    finally:
        if driver:  # Only attempt to quit if driver was initialized
            try:
                driver.quit()
                logger.info("Chrome driver closed successfully")
            except Exception as quit_error:
                logger.warning(f"Failed to close driver: {str(quit_error)}")
