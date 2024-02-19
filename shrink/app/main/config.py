from os import getenv

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = getenv("BOT_TOKEN")
DATABASE_URL = getenv("DATABASE_URL")
ADMIN_ID = getenv("ADMIN_ID")
