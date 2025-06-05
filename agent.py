import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import random
import logging
from datetime import datetime
# Создаём имя файла с датой, например: log_2025-06-01.txt
log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.txt"
error_log_filename = f"errors_{datetime.now().strftime('%Y-%m-%d')}.txt"

# Основной лог
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_filename, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Отдельный логгер для ошибок
error_handler = logging.FileHandler(error_log_filename, mode='a', encoding='utf-8')
error_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(error_handler)

logger = logging.getLogger(__name__)
logger.addHandler(error_handler)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Загружаем .env файл
load_dotenv(dotenv_path='secrets/keys.env')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Не знаешь как поступать? Поступай как знаешь.",
        "Если заблудился, то иди домой.",
        "Если тонешь, то плыви к берегу."
    ]
    await update.message.reply_text(random.choice(quotes))

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_question = update.message.text
    logger.info(f"User {user.username} (ID: {user.id}) asked: {user_question}")
    if not user_question:
        await update.message.reply_text("Бро, напиши вопрос после /ask :)")
        return

    try:

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты дружелюбный помощник."},
                {"role": "user", "content": user_question}
            ]
        )
        answer = response.choices[0].message.content
        logger.info(f"User question: {user_question}")
        logger.info(f"OpenAI response: {answer}")
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        await update.message.reply_text("Извините, произошла ошибка при обработке вашего запроса.")

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_command))

WEBHOOK_URL = "https://my-ai-bot-ehgw.onrender.com"  # ← свой URL Render

application.run_webhook(
    listen="0.0.0.0",
    port=int(os.getenv("PORT", 10000)),
    webhook_url=WEBHOOK_URL,
)