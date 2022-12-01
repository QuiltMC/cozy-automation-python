import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", None) is not None

TOKEN = os.getenv("TOKEN", "")
if not TOKEN:
    raise ValueError("TOKEN is not set")

LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
if not LOG_CHANNEL:
    raise ValueError("LOG_CHANNEL is not set")

GIT_SHA = os.getenv("GIT_SHA", "unknown")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG" if DEBUG else "INFO")
