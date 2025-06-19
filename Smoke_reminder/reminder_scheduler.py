import asyncio
import os
import json
from datetime import datetime, date
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение токена и USER_ID
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_ID_STR = os.getenv("USER_ID")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в файле .env")
if not USER_ID_STR:
    raise ValueError("USER_ID не найден в файле .env")

try:
    USER_ID = int(USER_ID_STR)
except ValueError:
    raise ValueError(f"USER_ID должен быть числом, получено: {USER_ID_STR}")

# Создание бота
bot = Bot(token=TELEGRAM_TOKEN)

# Настройка временной зоны Vancouver
vancouver_tz = pytz.timezone('America/Vancouver')

# Настройки для подсчета экономии
CIGARETTES_PER_DAY = 20  # Сколько сигарет курил в день
CIGARETTES_PER_PACK = 20  # Сигарет в пачке
PRICE_PER_PACK = 22  # Цена пачки в долларах (в Канаде)

# Файл для хранения данных о днях
DATA_FILE = "quit_smoking_data.json"


def load_data():
    """Загрузка данных о днях без курения"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Проверяем, есть ли дата начала
                if 'start_date' in data:
                    return data

        # Если файла нет или нет даты начала, создаем новый
        today = date.today().isoformat()
        data = {
            'start_date': today,
            'total_days': 0
        }
        save_data(data)
        return data
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        # Возвращаем данные по умолчанию
        today = date.today().isoformat()
        return {
            'start_date': today,
            'total_days': 0
        }


def save_data(data):
    """Сохранение данных о днях без курения"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")


def calculate_days_and_savings():
    """Подсчет дней без курения и сэкономленных денег"""
    data = load_data()

    # Вычисляем количество дней
    start_date = datetime.fromisoformat(data['start_date']).date()
    today = date.today()
    days_passed = (today - start_date).days + 1  # +1 чтобы первый день считался как день 1

    # Обновляем данные
    data['total_days'] = days_passed
    save_data(data)

    # Подсчет экономии
    total_cigarettes_not_smoked = days_passed * CIGARETTES_PER_DAY
    packs_not_bought = total_cigarettes_not_smoked / CIGARETTES_PER_PACK
    money_saved = packs_not_bought * PRICE_PER_PACK

    return days_passed, money_saved, total_cigarettes_not_smoked


def get_motivational_message(day_number):
    """Получение мотивационного сообщения в зависимости от дня"""
    if day_number == 1:
        return "Первый день - ты красавчик! 🌟"
    elif day_number == 2:
        return "Ого, уже второй день! Отлично держишься! 💪"
    elif day_number == 3:
        return "День третий - так держать! 🔥"
    elif day_number <= 7:
        return f"День {day_number} - неделя почти за плечами! 🚀"
    elif day_number <= 14:
        return f"День {day_number} - уже больше недели! Гордись собой! 🏆"
    elif day_number <= 30:
        return f"День {day_number} - месяц на горизонте! Невероятно! 🎯"
    elif day_number <= 90:
        return f"День {day_number} - ты уже профи! Месяц за плечами! 🎖️"
    else:
        return f"День {day_number} - ты легенда! Просто космос! 🌌"


async def send_daily_reminder():
    """Отправка ежедневного напоминания с подсчетом дней и экономии"""
    try:
        days, money_saved, cigarettes_not_smoked = calculate_days_and_savings()
        motivational_msg = get_motivational_message(days)

        # Форматирование сообщения
        message = f"""🚭 {motivational_msg}

💰 Сэкономлено: ${money_saved:.2f}
🚬 Не выкурено сигарет: {cigarettes_not_smoked}
📦 Не куплено пачек: {cigarettes_not_smoked / CIGARETTES_PER_PACK:.1f}

🏃‍♂️ Твоё здоровье благодарит тебя каждый день!"""

        await bot.send_message(chat_id=USER_ID, text=message)

        current_time = datetime.now(vancouver_tz)
        logger.info(f"Напоминание отправлено: День {days}, сэкономлено ${money_saved:.2f}, время: {current_time}")

    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневного напоминания: {e}")


async def setup_scheduler():
    """Настройка планировщика задач"""
    scheduler = AsyncIOScheduler(timezone=vancouver_tz)

    # Ежедневное напоминание в 6:40 утра Vancouver time
    scheduler.add_job(
        send_daily_reminder,
        CronTrigger(hour=6, minute=40, timezone=vancouver_tz),
        id='daily_reminder',
        name='Ежедневное напоминание о курении с подсчетом'
    )

    scheduler.start()
    logger.info("Планировщик запущен успешно")
    logger.info(f"Текущее время Vancouver: {datetime.now(vancouver_tz)}")
    logger.info("Запланированные задачи:")
    logger.info("- Ежедневное напоминание: 6:40 AM Vancouver time")

    return scheduler


async def main():
    """Основная функция"""
    try:
        # Проверка подключения к боту
        bot_info = await bot.get_me()
        logger.info(f"Бот подключен: @{bot_info.username}")

        # Загрузка данных и показ текущей статистики
        days, money_saved, cigarettes_not_smoked = calculate_days_and_savings()

        # Настройка планировщика
        scheduler = await setup_scheduler()

        # Отправка сообщения о запуске с текущей статистикой
        startup_message = f"""🤖 Бот запущен!

📊 Текущая статистика:
🗓️ Дней без курения: {days}
💰 Сэкономлено: ${money_saved:.2f}
🚬 Не выкурено: {cigarettes_not_smoked} сигарет

⏰ Ежедневные напоминания в 6:40 AM Vancouver time
🕒 Текущее время: {datetime.now(vancouver_tz).strftime('%H:%M:%S')}"""

        await bot.send_message(chat_id=USER_ID, text=startup_message)

        # Бесконечный цикл для поддержания работы бота
        logger.info("Бот работает... Нажмите Ctrl+C для остановки")
        while True:
            await asyncio.sleep(60)  # Проверка каждую минуту

    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        if 'scheduler' in locals():
            scheduler.shutdown()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())