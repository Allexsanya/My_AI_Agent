import asyncio
import os
import logging
from datetime import datetime
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from dotenv import load_dotenv

from bot_chat.chat_handler import setup_chat_handlers
from smoking_reminder.smoking_tracker import setup_smoking_scheduler, calculate_days_and_savings
from lina_water.water_reminder import setup_water_scheduler

# 🔧 Включаем tracemalloc для отладки
import tracemalloc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

tracemalloc.start()

# 🔧 Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Отключаем лишние логи
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

# 🔐 Загрузка переменных окружения
load_dotenv(dotenv_path='secrets/keys.env')

# Получение токенов и ID
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_ID_STR = os.getenv("USER_ID")
LINA_USER_ID_STR = os.getenv("LINA_USER_ID")

# Проверка обязательных переменных
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в файле .env")
if not USER_ID_STR:
    raise ValueError("USER_ID не найден в файле .env")

try:
    USER_ID = int(USER_ID_STR)
except ValueError:
    raise ValueError(f"USER_ID должен быть числом, получено: {USER_ID_STR}")

# ID для напоминаний о воде
LINA_USER_ID = None
if LINA_USER_ID_STR:
    try:
        LINA_USER_ID = int(LINA_USER_ID_STR)
    except ValueError:
        logger.warning(f"LINA_USER_ID должен быть числом, получено: {LINA_USER_ID_STR}")

# Настройки
vancouver_tz = pytz.timezone('America/Vancouver')
LOCAL_TEST = False
WEBHOOK_URL = "https://my-ai-bot-ehgw.onrender.com"


async def send_startup_message(bot):
    """Отправка сообщения о запуске бота"""
    try:
        days, money_saved, cigarettes_not_smoked = calculate_days_and_savings()
        startup_message = f"""🤖 Бот запущен!

📊 Текущая статистика курения:
🗓️ Дней без курения: {days}
💰 Сэкономлено: ${money_saved:.2f}
🚬 Не выкурено: {cigarettes_not_smoked} сигарет

⏰ Ежедневные напоминания в 6:40 AM Vancouver time
🕒 Текущее время: {datetime.now(vancouver_tz).strftime('%H:%M:%S')}"""

        await bot.send_message(chat_id=USER_ID, text=startup_message)
        logger.info("Стартовое сообщение отправлено")
    except Exception as e:
        logger.error(f"Ошибка при отправке стартового сообщения: {e}")


async def main():
    """Основная функция"""
    application = None
    scheduler = None

    try:
        # Настройка Telegram приложения
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Подключение обработчиков из модулей
        setup_chat_handlers(application)

        # Проверка подключения к боту
        bot_info = await application.bot.get_me()
        logger.info(f"Бот подключен: @{bot_info.username}")

        # Настройка планировщика
        scheduler = AsyncIOScheduler(timezone=vancouver_tz)

        # Подключение планировщиков из модулей
        setup_smoking_scheduler(scheduler, application.bot, USER_ID)
        if LINA_USER_ID:
            setup_water_scheduler(scheduler, application.bot, LINA_USER_ID)
            logger.info("Напоминания о воде включены")
        else:
            logger.info("Напоминания о воде отключены (LINA_USER_ID не установлен)")

        scheduler.start()
        logger.info("Планировщик запущен")
        logger.info(f"Текущее время Vancouver: {datetime.now(vancouver_tz)}")

        # Отправка сообщения о запуске
        await send_startup_message(application.bot)

        # Запуск в зависимости от режима
        if LOCAL_TEST:
            logger.info("🟡 LOCAL_TEST включён — запускаю run_polling()")
            await application.run_polling(drop_pending_updates=True)
        else:
            logger.info(f"🟢 PROD режим — запускаю run_webhook() на {WEBHOOK_URL}")
            await application.run_webhook(
                listen="0.0.0.0",
                port=int(os.getenv("PORT", 10000)),
                webhook_url=WEBHOOK_URL,
                drop_pending_updates=True
            )

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Корректная остановка
        if scheduler and scheduler.running:
            try:
                scheduler.shutdown(wait=False)
                logger.info("Планировщик остановлен")
            except Exception as e:
                logger.error(f"Ошибка при остановке планировщика: {e}")

        if application:
            try:
                await application.shutdown()
                logger.info("Приложение остановлено")
            except Exception as e:
                logger.error(f"Ошибка при остановке приложения: {e}")

        logger.info("Бот остановлен")


def run_bot():
    """Запуск бота с правильной обработкой event loop"""
    try:
        try:
            loop = asyncio.get_running_loop()
            logger.info("Обнаружен работающий event loop, используем его")
            import nest_asyncio
            nest_asyncio.apply()
            loop.run_until_complete(main())
        except RuntimeError:
            logger.info("Создаем новый event loop")
            asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка по Ctrl+C")
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_bot()