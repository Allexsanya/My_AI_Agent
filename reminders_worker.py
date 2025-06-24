import asyncio
from agent import main

if __name__ == "__main__":
    async def run_reminders():
        await main()  # Внутри main() уже вызывается scheduler.start()

    asyncio.run(run_reminders())