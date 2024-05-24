import base64
from os import getenv
from dotenv import load_dotenv
# from cryptography.fernet import Fernet

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
DATABASE_URL = getenv("DATABASE_URL")
ADMIN_ID = getenv("ADMIN_ID")
UKASSA_TOKEN = getenv("UKASSA_TOKEN")
PAYMASTER_TOKEN = getenv("PAYMASTER_TOKEN")

# key_str = getenv("KEY")
# key = base64.urlsafe_b64decode(key_str.encode())
# cipher_suite = Fernet(key)
