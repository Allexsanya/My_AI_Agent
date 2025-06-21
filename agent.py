import asyncio
import os
import logging
from datetime import datetime
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from dotenv import load_dotenv
load_dotenv()
import sys

# Добавляем путь к модулям (важно для Render)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_chat.chat_handler import setup_chat_handlers
from smoking_reminder.smoking_tracker import setup_smoking_scheduler, calculate_days_and_savings
from lina_water.water_reminder import setup_water_scheduler

# 🔧 Включаем tracemalloc
import tracemalloc
tracemalloc.start()

# 🔧 Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

# 🔐 .env
load_dotenv(dotenv_path='secrets/keys.env')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_ID = int(os.getenv("USER_ID", "0"))
LINA_USER_ID = int(os.getenv("LINA_USER_ID", "0")) if os.getenv("LINA_USER_ID") else None

if not TELEGRAM_TOKEN or USER_ID == 0:
    raise ValueError("❌ TELEGRAM_TOKEN или USER_ID не заданы!")

vancouver_tz = pytz.timezone('America/Vancouver')
WEBHOOK_URL = "https://my-ai-bot-ehgw.onrender.com"

# 🌞 Стартовое сообщение
async def send_startup_message(bot):
    try:
        days, money_saved, cigarettes_not_smoked = calculate_days_and_savings()
        msg = (
            f"🤖 Бот запущен!\n\n"
            f"📊 Статистика:\n"
            f"🗓️ Дней без курения: {days}\n"
            f"💰 Сэкономлено: ${money_saved:.2f}\n"
            f"🚬 Не выкурено: {cigarettes_not_smoked} сигарет\n\n"
            f"⏰ Напоминания в 6:40 AM (Vancouver)\n"
            f"🕒 Сейчас: {datetime.now(vancouver_tz).strftime('%H:%M:%S')}"
        )
        await bot.send_message(chat_id=USER_ID, text=msg)
    except Exception as e:
        logger.error(f"Ошибка старта: {e}")

# 🌐 Основной запуск
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    setup_chat_handlers(application)

    scheduler = AsyncIOScheduler(timezone=vancouver_tz)
    setup_smoking_scheduler(scheduler, application.bot, USER_ID)
    if LINA_USER_ID:
        setup_water_scheduler(scheduler, application.bot, LINA_USER_ID)

    scheduler.start()
    await send_startup_message(application.bot)

    logger.info(f"🟢 Запуск через Webhook: {WEBHOOK_URL}")
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    try:
        import nest_asyncio
        nest_asyncio.apply()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("⛔ Остановка по Ctrl+C")