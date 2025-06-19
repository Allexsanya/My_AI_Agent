import asyncio
import os
from datetime import datetime
from telegram import Bot
import pytz
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение токена и USER_ID
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
USER_ID_STR = os.getenv("USER_ID")

if not TELEGRAM_TOKEN:
    print("❌ TELEGRAM_TOKEN не найден в файле .env")
    exit(1)

if not USER_ID_STR:
    print("❌ USER_ID не найден в файле .env")
    exit(1)

try:
    USER_ID = int(USER_ID_STR)
except ValueError:
    print(f"❌ USER_ID должен быть числом, получено: {USER_ID_STR}")
    exit(1)

# Создание бота
bot = Bot(token=TELEGRAM_TOKEN)

# Временная зона Vancouver
vancouver_tz = pytz.timezone('America/Vancouver')


async def send_test_now():
    """Отправка тестового сообщения прямо сейчас"""
    try:
        current_time = datetime.now(vancouver_tz)
        message = f"🧪 ПРОВЕРКА! Время Vancouver: {current_time.strftime('%H:%M:%S %d.%m.%Y')}\n\n🚭 Ты красавчик что бросил курить!"

        print(f"⏳ Отправляю тестовое сообщение...")
        await bot.send_message(chat_id=USER_ID, text=message)
        print(f"✅ Тестовое сообщение успешно отправлено!")
        print(f"📱 Время отправки: {current_time.strftime('%H:%M:%S')}")

    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")


async def check_bot_connection():
    """Проверка подключения к боту"""
    try:
        bot_info = await bot.get_me()
        print(f"🤖 Бот подключен: @{bot_info.username}")
        print(f"📧 ID бота: {bot_info.id}")
        print(f"👤 Отправляю сообщение пользователю ID: {USER_ID}")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        return False


async def main():
    print("🔍 Проверка подключения к Telegram боту...")

    if await check_bot_connection():
        await send_test_now()
    else:
        print("❌ Не удалось подключиться к боту. Проверьте TELEGRAM_TOKEN")


if __name__ == "__main__":
    asyncio.run(main())