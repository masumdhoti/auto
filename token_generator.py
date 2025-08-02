# token_generator.py
import requests
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_token(username, password, otp_code):
    """Generate a GitHub personal access token."""
    # Validate OTP format (assuming GitHub OTP is 6 digits)
    if not otp_code.isdigit() or len(otp_code) != 6:
        logger.error(f"Invalid OTP format: {otp_code}")
        raise ValueError("OTP must be a 6-digit number")

    session = requests.Session()
    session.auth = (username, password)
    headers = {
        "X-GitHub-OTP": otp_code,
        "Accept": "application/vnd.github+json",
        "User-Agent": "Telegram-GitHub-Bot/1.0"
    }

    data = {
        "note": "Telegram Bot Access Token",
        "scopes": ["repo", "delete:packages", "admin:org", "delete_repo", "codespace"]
    }

    # Note: The /authorizations endpoint is deprecated. This is a placeholder.
    # Check GitHub's latest API for creating personal access tokens.
    url = "https://api.github.com/authorizations"

    for attempt in range(3):  # Retry up to 3 times
        try:
            logger.info(f"Attempting to generate token for {username} (attempt {attempt + 1})")
            res = session.post(url, json=data, headers=headers)
            
            if res.status_code == 201:
                logger.info(f"Token generated successfully for {username}")
                return res.json()["token"]
            elif res.status_code == 429:  # Rate limit
                retry_after = int(res.headers.get("Retry-After", 60))
                logger.warning(f"Rate limit hit, retrying after {retry_after} seconds")
                time.sleep(retry_after)
            else:
                logger.error(f"Failed to generate token: {res.status_code} - {res.text}")
                raise Exception(f"Failed to generate token: {res.status_code} - {res.text}")

        except Exception as e:
            if attempt == 2:
                logger.error(f"Final attempt failed for {username}: {str(e)}")
                raise
            time.sleep(2)  # Wait before retrying

    raise Exception("Failed to generate token after retries")