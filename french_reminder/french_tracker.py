import logging
import pytz
import random
import datetime
from apscheduler.triggers.cron import CronTrigger
import asyncio

# Настройка логирования
logger = logging.getLogger(__name__)

# Временная зона
vancouver_tz = pytz.timezone('America/Vancouver')


def get_french_study_reminder():
    """Получение напоминания о изучении французского"""
    french_reminders = [
        "🇫🇷 Bonsoir! Время изучать французский для TFSL теста! 📚✨",
        "📖 Salut! 15-20 минут французского - и ты ближе к своей цели! 🎯",
        "🇫🇷 C'est l'heure d'étudier! Время французского для Канады! 🍁",
        "📚 Bonjour! Каждый день изучения приближает к мечте! 🌟",
        "🇫🇷 Allons-y! Давай изучать французский для TFSL! 💪",
        "📖 Время французского! 15-20 минут для большой цели! 🚀",
        "🇫🇷 Bonne chance! Изучай французский для своего будущего! ❤️",
        "📚 Каждое слово на французском - шаг к жизни в Канаде! 🏔️",
        "🇫🇷 Étudions ensemble! Время вечернего французского! 🌙",
        "📖 Motivation française! Твой французский становится лучше каждый день! ⭐"
    ]
    return random.choice(french_reminders)


def get_tfsl_motivation():
    """Получение мотивационного сообщения о TFSL тесте"""
    tfsl_messages = [
        "🎯 TFSL Test: Каждый день учебы приближает к успеху!\n📈 Французский - это инвестиция в будущее!",
        "🇨🇦 Канада ждет! TFSL тест откроет двери к новой жизни!\n💼 Твой французский - ключ к успеху!",
        "📚 TFSL подготовка: постоянство важнее интенсивности!\n🌟 15-20 минут каждый день = большой результат!",
        "🎓 Французский для TFSL: ты можешь это сделать!\n🚀 Каждое занятие делает тебя сильнее!",
        "🏆 TFSL успех начинается с ежедневной практики!\n💪 Твоя настойчивость обязательно окупится!"
    ]
    return random.choice(tfsl_messages)


def get_french_study_tips():
    """Получение советов по изучению французского"""
    study_tips = [
        "💡 Совет: сегодня сосредоточься на грамматике - это основа TFSL теста!",
        "💡 Рекомендация: почитай вслух 5 минут - улучшай произношение!",
        "💡 Совет: повтори вчерашние слова перед изучением новых!",
        "💡 Tip: сделай 10 упражнений на времена глаголов!",
        "💡 Совет: послушай французскую речь 5 минут для тренировки слуха!",
        "💡 Рекомендация: напиши 3 предложения на французском о своем дне!",
        "💡 Совет: изучи 5 новых слов и используй их в предложениях!",
        "💡 Tip: повтори правила согласования времен - важно для TFSL!",
        "💡 Совет: прочитай один абзац на французском и переведи его!",
        "💡 Рекомендация: сделай упражнения на аудирование 10 минут!"
    ]
    return random.choice(study_tips)


def get_french_phrases():
    """Получение полезных французских фраз для мотивации"""
    phrases = [
        "🇫🇷 \"Petit à petit, l'oiseau fait son nid\" - Шаг за шагом птица вьет гнездо",
        "🇫🇷 \"Rome ne s'est pas faite en un jour\" - Рим построили не за один день",
        "🇫🇷 \"Vouloir, c'est pouvoir\" - Хотеть значит мочь",
        "🇫🇷 \"La patience est la clé du succès\" - Терпение - ключ к успеху",
        "🇫🇷 \"Qui veut voyager loin ménage sa monture\" - Кто хочет далеко ехать, бережет лошадь",
        "🇫🇷 \"L'avenir appartient à ceux qui se lèvent tôt\" - Будущее принадлежит тем, кто рано встает",
        "🇫🇷 \"Aide-toi, le ciel t'aidera\" - На Бога надейся, а сам не плошай"
    ]
    return random.choice(phrases)


async def send_french_study_reminder(bot, user_id):
    """Отправка ежедневного напоминания о французском"""
    try:
        # Определяем тип сообщения случайно
        message_type = random.choice(['simple', 'motivational', 'with_tip', 'with_phrase'])

        if message_type == 'simple':
            message = get_french_study_reminder()
        elif message_type == 'motivational':
            base_reminder = get_french_study_reminder()
            motivation = get_tfsl_motivation()
            message = f"{base_reminder}\n\n{motivation}"
        elif message_type == 'with_tip':
            base_reminder = get_french_study_reminder()
            tip = get_french_study_tips()
            message = f"{base_reminder}\n\n{tip}"
        else:  # with_phrase
            base_reminder = get_french_study_reminder()
            phrase = get_french_phrases()
            message = f"{base_reminder}\n\n{phrase}"

        await bot.send_message(chat_id=user_id, text=message)
        current_time = datetime.datetime.now(vancouver_tz)
        logger.info(f"Напоминание о французском отправлено в {current_time}")

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания о французском: {e}")


async def send_weekend_french_motivation(bot, user_id):
    """Отправка мотивационного сообщения на выходных"""
    weekend_messages = [
        "🌟 Выходные - отличное время для интенсивного изучения французского!\n🇫🇷 Можешь заниматься дольше обычного! 📚",
        "🎯 Weekend français! Сегодня можно уделить французскому больше времени!\n💪 TFSL тест приближается!",
        "🇫🇷 Викенд - время для французского марафона!\n📖 30-40 минут сегодня вместо обычных 15-20!",
        "🌈 Выходные = французские дни!\n🎓 Повтори всё изученное за неделю!"
    ]

    try:
        message = random.choice(weekend_messages)
        await bot.send_message(chat_id=user_id, text=message)
        logger.info("Мотивационное сообщение на выходных отправлено")
    except Exception as e:
        logger.error(f"Ошибка при отправке выходного напоминания: {e}")


async def send_weekly_progress_reminder(bot, user_id):
    """Еженедельное напоминание о прогрессе"""
    weekly_messages = [
        "📊 Неделя изучения французского завершена!\n🎯 Как прошла подготовка к TFSL тесту?\n💪 Продолжай в том же духе!",
        "🏆 Weekly French Check!\n📚 7 дней занятий = большой прогресс!\n🇫🇷 Français devient plus facile!",
        "⭐ Еженедельный отчет по французскому!\n🎓 Каждый день приближает к цели TFSL!\n🚀 Продолжай двигаться вперед!"
    ]

    try:
        message = random.choice(weekly_messages)
        await bot.send_message(chat_id=user_id, text=message)
        logger.info("Еженедельное напоминание о прогрессе отправлено")
    except Exception as e:
        logger.error(f"Ошибка при отправке еженедельного напоминания: {e}")


# Обёртки для планировщика
def french_study_reminder_wrapper(bot, user_id):
    """Синхронная обёртка для ежедневного напоминания"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_french_study_reminder(bot, user_id))
    finally:
        loop.close()


def weekend_french_motivation_wrapper(bot, user_id):
    """Синхронная обёртка для мотивации на выходных"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_weekend_french_motivation(bot, user_id))
    finally:
        loop.close()


def weekly_progress_reminder_wrapper(bot, user_id):
    """Синхронная обёртка для еженедельного напоминания"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_weekly_progress_reminder(bot, user_id))
    finally:
        loop.close()


def setup_french_scheduler(scheduler, bot, user_id):
    """Настройка планировщика для напоминаний о французском"""

    # Основное ежедневное напоминание в 22:15
    scheduler.add_job(
        french_study_reminder_wrapper,
        CronTrigger(hour=22, minute=15, timezone=vancouver_tz),
        args=[bot, user_id],
        id='daily_french_reminder',
        name='Ежедневное напоминание о французском'
    )

    # Дополнительное напоминание на выходных в 10:00 (суббота и воскресенье)
    scheduler.add_job(
        weekend_french_motivation_wrapper,
        CronTrigger(day_of_week='sat,sun', hour=10, minute=0, timezone=vancouver_tz),
        args=[bot, user_id],
        id='weekend_french_motivation',
        name='Мотивация на выходных'
    )

    # Еженедельное напоминание о прогрессе (воскресенье в 19:00)
    scheduler.add_job(
        weekly_progress_reminder_wrapper,
        CronTrigger(day_of_week='sun', hour=19, minute=0, timezone=vancouver_tz),
        args=[bot, user_id],
        id='weekly_french_progress',
        name='Еженедельный прогресс французского'
    )

    logger.info("Планировщик французского языка настроен:")
    logger.info("- Ежедневно: 22:15")
    logger.info("- Выходные: 10:00 (сб, вс)")
    logger.info("- Еженедельно: воскресенье 19:00")


# Функция для ручного тестирования
async def test_french_reminder(bot, user_id):
    """Тестовая функция для проверки напоминания о французском"""
    await send_french_study_reminder(bot, user_id)
    logger.info("Тестовое напоминание о французском отправлено")