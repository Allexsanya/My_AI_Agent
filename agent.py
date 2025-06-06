import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import random
from collections import defaultdict
import time
import logging
from datetime import datetime

# Убедимся, что папка logs существует
os.makedirs("logs", exist_ok=True)

log_filename = os.path.join("logs", f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
error_log_filename = os.path.join("logs", f"errors_{datetime.now().strftime('%Y-%m-%d')}.txt")

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


logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.INFO)
logger.addHandler(error_handler)
# Загружаем .env файл
load_dotenv(dotenv_path='secrets/keys.env')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

last_user_request = defaultdict(lambda: 0) # user_id -> timestamp

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Не знаешь как поступать? Поступай как знаешь.",
        "Если заблудился, то иди домой.",
        "Если тонешь, то плыви к берегу."
    ]
    await update.message.reply_text(random.choice(quotes))

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "NoUsername"
    user_text = update.message.text
    # 🔒 Ограничение по длине сообщения
    if len(user_text) > 500:
        await update.message.reply_text("😶 Слишком длинное сообщение, сократи, бро.")
        return

    # 🧹 Фильтрация по ключевым словам
    SPAM_KEYWORDS = ["crypto", "sex", "porn", "http", "nude", "casino", "bitcoin"]
    if any(word in user_text.lower() for word in SPAM_KEYWORDS):
        logger.warning(f"SPAM BLOCKED from {username} ({user_id}): {user_text}")
        await update.message.reply_text("🚫 Это сообщение похоже на спам.")
        return
    now = time.time()
    if now - last_user_request[user_id] < 10:
        await update.message.reply_text("Not so fast bro, I'm thinking")
        return
    last_user_request[user_id] = now
    user_question = update.message.text
    logger.info(f"[{username} | ID: {user_id}] -> {user_text}")
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
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "NoUsername"

    logger.info(f"[{username} | ID: {user_id}] sent /start")

    await update.message.reply_text("👋 Привет! Просто напиши сообщение, и я постараюсь ответить как умный бот!")

# Обработка команд
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", start_command))  # Пока одна функция на всё
application.run_webhook(
    listen="0.0.0.0",
    port=int(os.getenv("PORT", 10000)),
    webhook_url=WEBHOOK_URL,
)