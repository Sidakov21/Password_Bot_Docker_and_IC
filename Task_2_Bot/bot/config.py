import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "budget.db"
