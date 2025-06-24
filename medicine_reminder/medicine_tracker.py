import random
import logging
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
import pytz
import asyncio

# Настройка логирования
logger = logging.getLogger(__name__)

# Временная зона
helsinki_tz = pytz.timezone('Europe/Helsinki')


def get_medicine_reminder():
    """Получение напоминания о лекарствах"""
    medicine_reminders = [
        "💊 Мамочка, время принять лекарства! Не забывай о своем здоровье ❤️",
        "🩺 Напоминание: пора принять препараты! Твое здоровье важно 💕",
        "💊 Время лекарств! Береги себя, дорогая мама 🌸",
        "🩺 Не забудь про таблетки! Здоровье - это главное 💖",
        "💊 Мама, пора принять лекарства! Заботься о себе 🤗",
        "🩺 Время препаратов! Твое самочувствие очень важно ❤️",
        "💊 Напоминание о лекарствах! Будь здорова, мамуля 💐",
        "🩺 Пора принять таблетки! Береги свое здоровье 🌺",
        "💊 Время лечения! Не пропускай прием лекарств 💝",
        "🩺 Мамочка, твои препараты ждут! Заботься о себе 🌹"
    ]
    return random.choice(medicine_reminders)


def get_motivational_medicine_message():
    """Получение мотивационного сообщения о важности лекарств"""
    motivational_messages = [
        "💊 Регулярный прием лекарств - залог хорошего самочувствия! 🌟\nТвое здоровье бесценно ❤️",
        "🩺 Каждая таблетка - это забота о твоем будущем! 💖\nПродолжай заботиться о себе 🌸",
        "💊 Постоянство в лечении приводит к отличным результатам! 🎯\nТы молодец, что следишь за здоровьем! 💕",
        "🩺 Твое здоровье - это подарок всей семье! 🎁\nСпасибо, что заботишься о себе ❤️",
        "💊 Регулярность - ключ к успешному лечению! 🗝️\nПродолжай в том же духе! 🌺",
    ]
    return random.choice(motivational_messages)


def get_health_tips():
    """Получение полезных советов о здоровье"""
    health_tips = [
        "💡 Совет: принимай лекарства в одно и то же время для лучшего эффекта!",
        "💡 Помни: запивай таблетки достаточным количеством воды!",
        "💡 Совет: веди дневник приема лекарств - это поможет врачу!",
        "💡 Важно: не пропускай прием, даже если чувствуешь себя хорошо!",
        "💡 Помни: если есть вопросы о лекарствах - обращайся к врачу!",
        "💡 Совет: храни препараты в прохладном сухом месте!",
        "💡 Важно: проверяй срок годности лекарств регулярно!"
    ]
    return random.choice(health_tips)


async def send_medicine_reminder(bot, user_id):
    """Отправка обычного напоминания о лекарствах"""
    try:
        # 70% обычное напоминание, 30% с мотивацией или советом
        if random.random() < 0.7:
            message = get_medicine_reminder()
        else:
            if random.random() < 0.5:
                message = get_motivational_medicine_message()
            else:
                base_reminder = get_medicine_reminder()
                tip = get_health_tips()
                message = f"{base_reminder}\n\n{tip}"

        await bot.send_message(chat_id=user_id, text=message)
        current_time = datetime.now(helsinki_tz)
        logger.info(f"Напоминание о лекарствах отправлено в {current_time}")

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о лекарствах: {e}")


async def send_morning_medicine_reminder(bot, user_id):
    """Утреннее напоминание о лекарствах"""
    morning_messages = [
        "🌅 Доброе утро, мамочка! Начни день с заботы о здоровье - прими утренние лекарства! ☀️💊",
        "🌄 Утро - лучшее время для заботы о себе! Не забудь про препараты! 💕",
        "☀️ Новый день начинается с заботы о здоровье! Время утренних лекарств! 🌸",
        "🌅 Доброе утро! Пусть день начнется с правильной заботы о себе! 💊❤️"
    ]

    try:
        message = random.choice(morning_messages)
        await bot.send_message(chat_id=user_id, text=message)
        logger.info("Утреннее напоминание о лекарствах отправлено")
    except Exception as e:
        logger.error(f"Ошибка при отправке утреннего напоминания: {e}")


async def send_evening_medicine_reminder(bot, user_id):
    """Вечернее напоминание о лекарствах"""
    evening_messages = [
        "🌆 Вечер - время позаботиться о здоровье! Прими вечерние лекарства! 💊✨",
        "🌙 Заверши день заботой о себе - время вечерних препаратов! 💕",
        "🌇 Вечернее напоминание: твое здоровье в твоих руках! 💊🌟",
        "🌆 Пусть вечер пройдет с пользой для здоровья! Время лекарств! ❤️"
    ]

    try:
        message = random.choice(evening_messages)
        await bot.send_message(chat_id=user_id, text=message)
        logger.info("Вечернее напоминание о лекарствах отправлено")
    except Exception as e:
        logger.error(f"Ошибка при отправке вечернего напоминания: {e}")


# Обёртки для планировщика
def medicine_reminder_wrapper(bot, user_id):
    """Синхронная обёртка для обычного напоминания"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_medicine_reminder(bot, user_id))
    finally:
        loop.close()


def morning_medicine_wrapper(bot, user_id):
    """Синхронная обёртка для утреннего напоминания"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_morning_medicine_reminder(bot, user_id))
    finally:
        loop.close()


def evening_medicine_wrapper(bot, user_id):
    """Синхронная обёртка для вечернего напоминания"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_evening_medicine_reminder(bot, user_id))
    finally:
        loop.close()


def setup_medicine_scheduler(scheduler, bot, user_id):
    """Настройка планировщика для напоминаний о лекарствах"""

    # Утренние напоминания
    # 8:00 - основное утреннее напоминание
    scheduler.add_job(
        morning_medicine_wrapper,
        CronTrigger(hour=8, minute=0, timezone=helsinki_tz),
        args=[bot, user_id],
        id='morning_medicine_reminder',
        name='Утреннее напоминание о лекарствах'
    )

    # 8:30 - дополнительное утреннее напоминание
    scheduler.add_job(
        medicine_reminder_wrapper,
        CronTrigger(hour=8, minute=30, timezone=helsinki_tz),
        args=[bot, user_id],
        id='morning_medicine_reminder_2',
        name='Дополнительное утреннее напоминание'
    )

    # Дневные напоминания
    # 14:00 - дневное напоминание
    scheduler.add_job(
        medicine_reminder_wrapper,
        CronTrigger(hour=14, minute=0, timezone=helsinki_tz),
        args=[bot, user_id],
        id='afternoon_medicine_reminder',
        name='Дневное напоминание о лекарствах'
    )

    # Вечерние напоминания
    # 20:00 - основное вечернее напоминание
    scheduler.add_job(
        evening_medicine_wrapper,
        CronTrigger(hour=20, minute=0, timezone=helsinki_tz),
        args=[bot, user_id],
        id='evening_medicine_reminder',
        name='Вечернее напоминание о лекарствах'
    )

    # 20:30 - дополнительное вечернее напоминание
    scheduler.add_job(
        medicine_reminder_wrapper,
        CronTrigger(hour=20, minute=30, timezone=helsinki_tz),
        args=[bot, user_id],
        id='evening_medicine_reminder_2',
        name='Дополнительное вечернее напоминание'
    )

    logger.info("Планировщик напоминаний о лекарствах настроен:")
    logger.info("- Утром: 8:00, 8:30")
    logger.info("- Днем: 14:00")
    logger.info("- Вечером: 20:00, 20:30")


# Функция для ручного тестирования
async def test_medicine_reminder(bot, user_id):
    """Тестовая функция для проверки напоминания о лекарствах"""
    await send_medicine_reminder(bot, user_id)
    logger.info("Тестовое напоминание о лекарствах отправлено")