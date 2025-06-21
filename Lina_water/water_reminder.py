import random
import logging
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
import pytz

# Настройка логирования
logger = logging.getLogger(__name__)

# Временная зона
vancouver_tz = pytz.timezone('America/Vancouver')


def get_water_reminder():
    """Получение случайного напоминания о воде"""
    water_quotes = [
        "💧 Пить нужно часто! Глотни водички 😊",
        "🌊 А не засохнешь? Время попить воды!",
        "💦 Твой организм просит воды! Не забывай пить",
        "🥤 Гидратация - это важно! Выпей стаканчик воды",
        "💧 Вода - источник жизни! Время освежиться",
        "🌊 Почки скажут спасибо за стакан воды!",
        "💦 Кожа будет благодарна за глоток воды",
        "🥛 Не дай себе засохнуть! Пей больше воды",
        "💧 Время водной паузы! Выпей немного воды",
        "🌊 Вода помогает мозгу работать лучше! Попей",
        "💦 Маленький глоток - большая польза!",
        "🥤 Помни: 8 стаканов в день - это норма!",
        "💧 Каждая клеточка твоего тела просит воды!",
        "🌊 Выпей воды и почувствуй прилив энергии!",
        "💦 Водичка поможет коже сиять! ✨",
        "🥛 Глоток воды = забота о себе 💕",
        "💧 Не забывай: ты на 60% состоишь из воды!",
        "🌊 Время гидратации! Твой организм скажет спасибо",
        "💦 Вода - лучший напиток для красоты и здоровья!",
        "🥤 Маленький перерыв на воду - большая польза!",
        "💧 Пей воду и будь здоровой! 🌸",
        "🌊 Каждый глоток воды - инвестиция в здоровье!",
        "💦 Время освежиться! Попей водички 😌",
        "🥛 Вода - твой лучший друг для хорошего самочувствия!"
    ]
    return random.choice(water_quotes)


def get_motivational_water_message():
    """Получение мотивационного сообщения о воде с фактами"""
    facts = [
        "💧 Факт: Даже 2% обезвоживания может снизить концентрацию на 30%!",
        "🌊 Знала ли ты? Вода помогает выводить токсины через почки!",
        "💦 Интересно: Достаточное количество воды улучшает настроение!",
        "🥤 Факт: Вода ускоряет метаболизм на 30% в течение часа!",
        "💧 Знала ли ты? Недостаток воды - частая причина усталости!",
        "🌊 Факт: Кожа на 64% состоит из воды - пей для красоты!",
        "💦 Интересно: Мозг на 75% состоит из воды!",
        "🥛 Факт: Вода помогает суставам оставаться здоровыми!"
    ]

    reminder = get_water_reminder()
    fact = random.choice(facts)

    return f"{reminder}\n\n{fact}"


async def send_water_reminder(bot, user_id):
    """Отправка напоминания о воде"""
    try:
        # Случайно выбираем обычное или мотивационное сообщение
        if random.random() < 0.3:  # 30% шанс на мотивационное сообщение
            message = get_motivational_water_message()
        else:
            message = get_water_reminder()

        await bot.send_message(chat_id=user_id, text=message)
        current_time = datetime.now(vancouver_tz)
        logger.info(f"Напоминание о воде отправлено в {current_time}")

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о воде: {e}")


async def send_special_water_reminder(bot, user_id):
    """Специальное напоминание о воде в определенное время"""
    special_messages = [
        "🌅 Доброе утро! Начни день со стакана воды! 💧",
        "☀️ Обеденное время! Не забудь про водичку! 🥤",
        "🌇 Вечер - время расслабиться с чашкой травяного чая или воды! 💦",
        "🌙 Перед сном - последний глоток воды для хорошего сна! 😴"
    ]

    current_hour = datetime.now(vancouver_tz).hour

    if 6 <= current_hour < 12:
        message = special_messages[0]  # Утро
    elif 12 <= current_hour < 17:
        message = special_messages[1]  # День
    elif 17 <= current_hour < 22:
        message = special_messages[2]  # Вечер
    else:
        message = special_messages[3]  # Ночь

    try:
        await bot.send_message(chat_id=user_id, text=message)
        logger.info(f"Специальное напоминание о воде отправлено: {current_hour}:00")
    except Exception as e:
        logger.error(f"Ошибка при отправке специального напоминания: {e}")


def should_send_reminder():
    """Определение, нужно ли отправлять напоминание (исключаем ночные часы)"""
    current_hour = datetime.now(vancouver_tz).hour
    # Отправляем напоминания только с 7:00 до 22:00
    return 7 <= current_hour <= 22


async def hourly_water_check(bot, user_id):
    """Проверка каждый час - отправлять ли напоминание"""
    if should_send_reminder():
        await send_water_reminder(bot, user_id)
    else:
        logger.info("Ночное время - напоминание о воде пропущено")


def setup_water_scheduler(scheduler, bot, user_id):
    """Настройка планировщика для напоминаний о воде"""

    # Основные ежечасные напоминания (с 7:00 до 22:00)
    scheduler.add_job(
        lambda: hourly_water_check(bot, user_id),
        CronTrigger(minute=0, timezone=vancouver_tz),
        id='hourly_water_reminder',
        name='Ежечасное напоминание о воде'
    )

    # Специальные напоминания в ключевые моменты дня
    # Утреннее напоминание (7:30)
    scheduler.add_job(
        lambda: send_special_water_reminder(bot, user_id),
        CronTrigger(hour=7, minute=30, timezone=vancouver_tz),
        id='morning_water_reminder',
        name='Утреннее напоминание о воде'
    )

    # Обеденное напоминание (12:30)
    scheduler.add_job(
        lambda: send_special_water_reminder(bot, user_id),
        CronTrigger(hour=12, minute=30, timezone=vancouver_tz),
        id='lunch_water_reminder',
        name='Обеденное напоминание о воде'
    )

    # Вечернее напоминание (18:30)
    scheduler.add_job(
        lambda: send_special_water_reminder(bot, user_id),
        CronTrigger(hour=18, minute=30, timezone=vancouver_tz),
        id='evening_water_reminder',
        name='Вечернее напоминание о воде'
    )

    logger.info("Планировщик напоминаний о воде настроен:")
    logger.info("- Ежечасно с 7:00 до 22:00")
    logger.info("- Специальные: 7:30, 12:30, 18:30")


# Функция для ручного тестирования
async def test_water_reminder(bot, user_id):
    """Тестовая функция для проверки напоминания о воде"""
    await send_water_reminder(bot, user_id)
    logger.info("Тестовое напоминание о воде отправлено")