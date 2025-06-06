import os
import logging
from datetime import datetime
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import random
import time
from collections import defaultdict

# 🔧 Логгер
os.makedirs("logs", exist_ok=True)
log_filename = os.path.join("logs", f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
error_log_filename = os.path.join("logs", f"errors_{datetime.now().strftime('%Y-%m-%d')}.txt")

logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

log_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
log_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

error_handler = logging.FileHandler(error_log_filename, mode='a', encoding='utf-8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

logger.addHandler(log_handler)
logger.addHandler(console_handler)
logger.addHandler(error_handler)

logger.info("✅ Логгер инициализирован. Запись идёт в файл и консоль.")

# 🔐 Загрузка переменных
load_dotenv(dotenv_path='secrets/keys.env')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)
last_user_request = defaultdict(lambda: 0)  # user_id -> timestamp

# 🎯 Команда /quote
async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Не знаешь как поступать? Поступай как знаешь.",
        "Если заблудился, то иди домой.",
        "Если тонешь, то плыви к берегу."
    ]
    await update.message.reply_text(random.choice(quotes))

# 🤖 Основной обработчик
async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "NoUsername"
    user_text = update.message.text

    # 🧹 Спам-фильтрация
    if len(user_text) > 500:
        await update.message.reply_text("😶 Слишком длинное сообщение, сократи, бро.")
        return

    if "http" in user_text.lower() or "@" in user_text:
        logger.warning(f"🔗 LINK/SPAM from {username} ({user_id}): {user_text}")
        await update.message.reply_text("🚫 Ссылки и упоминания запрещены.")
        return

    SPAM_KEYWORDS = ["crypto", "sex", "porn", "nude", "casino", "bitcoin"]
    if any(word in user_text.lower() for word in SPAM_KEYWORDS):
        logger.warning(f"SPAM BLOCKED from {username} ({user_id}): {user_text}")
        await update.message.reply_text("🚫 Это сообщение похоже на спам.")
        return

    # ⏱ Антифлуд
    now = time.time()
    if now - last_user_request[user_id] < 10:
        await update.message.reply_text("Not so fast bro, I'm thinking")
        return
    last_user_request[user_id] = now

    logger.info(f"[{username} | ID: {user_id}] -> {user_text}")
    user_question = update.message.text
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

# 🌍 Webhook URL
WEBHOOK_URL = "https://my-ai-bot-ehgw.onrender.com"

# 📌 Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "NoUsername"
    logger.info(f"[{username} | ID: {user_id}] sent /start")
    await update.message.reply_text("👋 Привет! Просто напиши сообщение, и я постараюсь ответить как умный бот!")

# 🛠️ Telegram приложение
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_command))
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("help", start_command))
application.add_handler(CommandHandler("quote", quote_command))

# 🚀 Запуск
application.run_webhook(
    listen="0.0.0.0",
    port=int(os.getenv("PORT", 10000)),
    webhook_url=WEBHOOK_URL,
)