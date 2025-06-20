import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import random
import time
from collections import defaultdict
from Smoke_reminder.reminder_scheduler import setup_scheduler as setup_smoke_scheduler

async def start_bot():
    await setup_smoke_scheduler()  # запуск напоминалки

    if LOCAL_TEST:
        logger.info("🟡 LOCAL_TEST включён — запускаю run_polling()")
        await application.run_polling()
    else:
        logger.info(f"🟢 PROD режим — запускаю run_webhook() на {WEBHOOK_URL}")
        await application.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 10000)),
            webhook_url=WEBHOOK_URL,
        )

# 🔧 Логгер (консоль для Render + file)
logger = logging.getLogger("telegram_bot")
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler('logs/agent.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("✅ Логгер инициализирован. Запись идёт в консоль и файл.")

# 🔐 Загрузка переменных
load_dotenv(dotenv_path='secrets/keys.env')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)
last_user_request = defaultdict(lambda: 0)  # user_id -> timestamp
# Local flag test
LOCAL_TEST = False # put true for local run, falls for render

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

# 📤 Команда /logs
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧾 Логи доступны только в Render → Logs → All logs.\nБот работает на Render, поэтому лог-файлы не сохраняются локально.")

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
application.add_handler(CommandHandler("logs", logs_command))

# 🚀 Запуск

if LOCAL_TEST:
    logger.info("🟡 LOCAL_TEST включён — запускаю run_polling()")
    application.run_polling()
else:
    logger.info(f"🟢 PROD режим — запускаю run_webhook() на {WEBHOOK_URL}")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )
# from venv.Smoke_reminder.reminder_scheduler import setup_scheduler
# setup_scheduler()
import asyncio

if __name__ == "__main__":
    asyncio.run(start_bot())