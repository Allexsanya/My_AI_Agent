import openai
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text("Привет! Я бот с OpenAI. Задай мне любой вопрос!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_text = update.message.text

    try:
        # Запрос к OpenAI
        messages = [
            {
                "role": "system",
                "content": "Ты дружелюбный и умный помощник. Отвечай кратко и по делу, но с юмором когда уместно. Говори на русском языке."
            },
            {
                "role": "user",
                "content": user_text
            }
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
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
            "🤔 Кажется, что-то пошло не так с моими мозгами!",
            "⚠️ Произошла ошибка при обработке запроса.",
            "🔧 Технические неполадки, попробуй еще раз через минуту.",
            "💭 Что-то сломалось, но я работаю над этим!"
        ]

        import random
        await update.message.reply_text(random.choice(error_messages))


def setup_chat_handlers(application):
    """Настройка обработчиков чата"""
    # Команды
    application.add_handler(CommandHandler("start", start))

    # Обработка текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Chat handlers настроены")