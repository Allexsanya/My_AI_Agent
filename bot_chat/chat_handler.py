import os
import logging
import random
import time
from collections import defaultdict
from openai import OpenAI
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from dotenv import load_dotenv

# Настройка логирования
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv(dotenv_path='secrets/keys.env')

# Получение API ключей
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден в файле .env")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
last_user_request = defaultdict(lambda: 0)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "NoUsername"
    logger.info(f"[{username} | ID: {user_id}] sent /start")
    await update.message.reply_text("👋 Привет! Просто напиши сообщение, и я постараюсь ответить как умный бот!")

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Не знаешь как поступать? Поступай как знаешь.",
        "Если заблудился, то иди домой.",
        "Если тонешь, то плыви к берегу.",
        "Главное - не паниковать и идти вперед.",
        "Каждый день - новая возможность стать лучше.",
        "Успех - это идти от неудачи к неудаче, не теряя энтузиазма.",
        "Не бойся медленно идти, бойся стоять на месте.",
        "Лучший способ предсказать будущее - создать его."
    ]
    await update.message.reply_text(random.choice(quotes))

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧾 Логи доступны только в Render → Logs → All logs.\n"
        "Бот работает на Render, поэтому лог-файлы не сохраняются локально."
    )

def setup_chat_handlers(application):
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("quote", quote_command))
    application.add_handler(CommandHandler("logs", logs_command))