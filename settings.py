# settings.py
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

GUILD_ID = os.environ.get("GUILD_ID")
ROLE_MESSAGE_ID = os.environ.get("ROLE_MESSAGE_ID")
VERIFIED_ROLE_ID = os.environ.get("VERIFIED_ROLE_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")