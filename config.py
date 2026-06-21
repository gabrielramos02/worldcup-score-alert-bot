
import os
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Falta el TELEGRAM_TOKEN en el archivo .env")


