import os
import logging
import random
import time
from collections import defaultdict
from openai import OpenAI
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Настройка логирования
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv(dotenv_path='secrets/keys.env')

# Получение API ключей
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден в файле .env")

# Создание клиента OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Антифлуд
last_user_request = defaultdict(lambda: 0)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    user_id = user.id
    username = user.username or "NoUsername"
    logger.info(f"[{username} | ID: {user_id}] sent /start")
    await update.message.reply_text("👋 Привет! Просто напиши сообщение, и я постараюсь ответить как умный бот!")


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /quote - случайная цитата"""
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
    """Команда /logs - информация о логах"""
    await update.message.reply_text(
        "🧾 Логи доступны только в Render → Logs → All logs.\n"
        "Бот работает на Render, поэтому лог-файлы не сохраняются локально."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - помощь"""
    help_text = """🤖 Доступные команды:

/start - Приветствие
/help - Эта справка
/quote - Случайная цитата
/logs - Информация о логах

Просто напиши любое сообщение, и я отвечу с помощью ИИ! ✨"""

    await update.message.reply_text(help_text)


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений через OpenAI"""
    user = update.effective_user
    user_id = user.id
    username = user.username or "NoUsername"
    user_text = update.message.text

    # Спам-фильтрация
    if len(user_text) > 500:
        await update.message.reply_text("😶 Слишком длинное сообщение, сократи, бро.")
        return

    if "http" in user_text.lower() or "@" in user_text:
        logger.warning(f"🔗 LINK/SPAM from {username} ({user_id}): {user_text}")
        await update.message.reply_text("🚫 Ссылки и упоминания запрещены.")
        return

    SPAM_KEYWORDS = ["crypto", "sex", "porn", "nude", "casino", "bitcoin", "gambling"]
    if any(word in user_text.lower() for word in SPAM_KEYWORDS):
        logger.warning(f"SPAM BLOCKED from {username} ({user_id}): {user_text}")
        await update.message.reply_text("🚫 Это сообщение похоже на спам.")
        return

    # Антифлуд
    now = time.time()
    if now - last_user_request[user_id] < 10:
        await update.message.reply_text("⏳ Не так быстро, бро! Подожди немного...")
        return
    last_user_request[user_id] = now

    logger.info(f"[{username} | ID: {user_id}] -> {user_text}")

    try:
        # Отправка индикатора "печатает"
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Запрос к OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты дружелюбный и умный помощник. Отвечай кратко и по делу, но с юмором когда уместно. Говори на русском языке."
                },
                {"role": "user", "content": user_text}
            ],
            max_tokens=500,
            temperature=0.7
        )

        answer = response.choices[0].message.content
        logger.info(f"User question: {user_text}")
        logger.info(f"OpenAI response: {answer}")

        # Отправка ответа
        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        error_messages = [
            "🤖 Извини, что-то пошло не так с моими мозгами!",
            "⚠️ Произошла ошибка при обработке запроса.",
            "🔧 Технические неполадки, попробуй еще раз через минуту.",
            "❌ Что-то сломалось, но я работаю над этим!"
        ]
        await update.message.reply_text(random.choice(error_messages))


def setup_chat_handlers(application):
    """Настройка обработчиков чата"""
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quote", quote_command))
    application.add_handler(CommandHandler("logs", logs_command))

    # Обработка текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_command))

    logger.info("Chat handlers настроены")