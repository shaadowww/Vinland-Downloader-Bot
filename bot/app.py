import logging
import asyncio

from aiogram import Bot, Dispatcher

from bot.handlers import router

from bot.backend import FakeDownloader

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)

# Initialize bot and dispatcher
if not settings.BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
downloader = FakeDownloader(workers=3, queue_size=10)


dp.include_router(router)

async def main():
    asyncio.create_task(downloader.start_workers())
    await dp.start_polling(bot, downloader=downloader)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("The bot work is stopping...")
