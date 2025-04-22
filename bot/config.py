import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
LOG_CHAT_ID = str(os.getenv("LOG_CHAT_ID"))
VK_CLOUD_TOKEN=str(os.getenv("VK_CLOUD_TOKEN"))
VK_CLOUD_HOST=str(os.getenv("VK_CLOUD_HOST"))
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
TIMER_TIME = int(os.getenv("TIMER_TIME"))
EXAMPLE_IDS = os.getenv("EXAMPLE_IDS").split(",")

