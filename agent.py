import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здорова, бро, я твой помощник!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я могу: /start, /help, /status, /motivate, /joke, /quote, /ask")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Я онлайн и готов помогать!")

async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Never give up!")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
        "Что сказал Python-программист, когда его код сработал с первого раза? —Этого не может быть!",
        "Почему коты — лучшие программисты? Потому что они отлично работают с пай (паузам).",
        "Anhelina gotovit vkusniy borsch"
    ]
    await update.message.reply_text(random.choice(jokes))

async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Не знаешь как поступать? Поступай как знаешь.",
        "Если заблудился, то иди домой.",
        "Если тонешь, то плыви к берегу."
    ]
    await update.message.reply_text(random.choice(quotes))

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_question = ' '.join(context.args)
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

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("status", status_command))
app.add_handler(CommandHandler("motivate", motivate_command))
app.add_handler(CommandHandler("joke", joke_command))
app.add_handler(CommandHandler("quote", quote_command))
app.add_handler(CommandHandler("ask", ask_command))

print("Бот запущен!")
app.run_polling()