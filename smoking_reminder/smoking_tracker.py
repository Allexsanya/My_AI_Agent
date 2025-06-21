import os
import json
import logging
from datetime import datetime, date
from apscheduler.triggers.cron import CronTrigger
import pytz

# Настройка логирования
logger = logging.getLogger(__name__)

# Настройки для курения
CIGARETTES_PER_DAY = 20
CIGARETTES_PER_PACK = 20
PRICE_PER_PACK = 22
DATA_FILE = "smoking_reminder/quit_smoking_data.json"

# Временная зона
vancouver_tz = pytz.timezone('America/Vancouver')


def load_data():
    """Загрузка данных о днях без курения"""
    try:
        # Создаем папку если не существует
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'start_date' in data:
                    return data

        today = date.today().isoformat()
        data = {
            'start_date': today,
            'total_days': 0,
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
        return data
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        today = date.today().isoformat()
        return {
            'start_date': today,
            'total_days': 0,
            'created_at': datetime.now().isoformat()
        }


def save_data(data):
    """Сохранение данных о днях без курения"""
    try:
        # Создаем папку если не существует
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")


def calculate_days_and_savings():
    """Подсчет дней без курения и сэкономленных денег"""
    data = load_data()
    start_date = datetime.fromisoformat(data['start_date']).date()
    today = date.today()
    days_passed = (today - start_date).days + 1

    # Обновляем данные
    data['total_days'] = days_passed
    data['last_calculated'] = datetime.now().isoformat()
    save_data(data)

    # Расчеты
    total_cigarettes_not_smoked = days_passed * CIGARETTES_PER_DAY
    packs_not_bought = total_cigarettes_not_smoked / CIGARETTES_PER_PACK
    money_saved = packs_not_bought * PRICE_PER_PACK

    return days_passed, money_saved, total_cigarettes_not_smoked


def get_motivational_message(day_number):
    """Получение мотивационного сообщения в зависимости от дня"""
    messages = {
        1: "Первый день - ты красавчик! 🌟",
        2: "Ого, уже второй день! Отлично держишься! 💪",
        3: "День третий - так держать! 🔥",
        7: "Неделя без курения! Невероятно! 🚀",
        14: "Две недели! Ты просто молодец! 🏆",
        30: "Месяц без курения! Легенда! 🎯",
        60: "Два месяца! Ты профи! 🎖️",
        90: "Три месяца! Просто космос! 🌌",
        180: "Полгода! Ты герой! 🦸‍♂️",
        365: "ГОД БЕЗ КУРЕНИЯ! ЧЕМПИОН! 🏅"
    }

    # Если есть точное совпадение дня
    if day_number in messages:
        return messages[day_number]

    # Иначе выбираем по диапазонам
    if day_number <= 7:
        return f"День {day_number} - неделя почти за плечами! 🚀"
    elif day_number <= 14:
        return f"День {day_number} - уже больше недели! Гордись собой! 🏆"
    elif day_number <= 30:
        return f"День {day_number} - месяц на горизонте! Невероятно! 🎯"
    elif day_number <= 90:
        return f"День {day_number} - ты уже профи! Месяц за плечами! 🎖️"
    elif day_number <= 180:
        return f"День {day_number} - полгода почти рядом! 🌟"
    elif day_number <= 365:
        return f"День {day_number} - год на горизонте! Легенда! 🌌"
    else:
        years = day_number // 365
        remaining_days = day_number % 365
        return f"День {day_number} ({years} лет {remaining_days} дней) - ты абсолютная легенда! 🏅"


def get_health_benefit(day_number):
    """Получение информации о пользе для здоровья"""
    if day_number == 1:
        return "🫁 Через 20 минут пульс и давление нормализуются!"
    elif day_number == 2:
        return "👃 Вкус и запах уже начинают восстанавливаться!"
    elif day_number == 3:
        return "💪 Дыхание становится легче, энергии больше!"
    elif day_number <= 7:
        return "🔋 Никотин полностью вышел из организма!"
    elif day_number <= 14:
        return "🏃‍♂️ Кровообращение улучшается, легче заниматься спортом!"
    elif day_number <= 30:
        return "🫁 Функция легких улучшается на 30%!"
    elif day_number <= 90:
        return "❤️ Риск сердечного приступа значительно снижен!"
    elif day_number <= 365:
        return "🩺 Риск инсульта снизился в 2 раза!"
    else:
        return "🌟 Твой организм благодарит тебя каждый день!"


async def send_daily_smoking_reminder(bot, user_id):
    """Отправка ежедневного напоминания о курении"""
    try:
        days, money_saved, cigarettes_not_smoked = calculate_days_and_savings()
        motivational_msg = get_motivational_message(days)
        health_benefit = get_health_benefit(days)

        # Расчет дополнительных метрик
        packs_not_bought = cigarettes_not_smoked / CIGARETTES_PER_PACK

        message = f"""🚭 {motivational_msg}

📊 Статистика за {days} дней:
💰 Сэкономлено: ${money_saved:.2f}
🚬 Не выкурено: {cigarettes_not_smoked} сигарет
📦 Не куплено: {packs_not_bought:.1f} пачек

{health_benefit}

🏃‍♂️ Продолжай в том же духе!"""

        await bot.send_message(chat_id=user_id, text=message)
        current_time = datetime.now(vancouver_tz)
        logger.info(f"Напоминание о курении отправлено: День {days}, время: {current_time}")

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о курении: {e}")


def setup_smoking_scheduler(scheduler, bot, user_id):
    """Настройка планировщика для напоминаний о курении"""
    # Ежедневное напоминание о курении в 6:40 утра Vancouver time
    scheduler.add_job(
        lambda: send_daily_smoking_reminder(bot, user_id),
        CronTrigger(hour=6, minute=40, timezone=vancouver_tz),
        id='daily_smoking_reminder',
        name='Ежедневное напоминание о курении'
    )

    logger.info("Планировщик курения настроен: 6:40 AM Vancouver time")


# Функция для ручного тестирования
async def test_smoking_reminder(bot, user_id):
    """Тестовая функция для проверки напоминания"""
    await send_daily_smoking_reminder(bot, user_id)
    logger.info("Тестовое напоминание отправлено")