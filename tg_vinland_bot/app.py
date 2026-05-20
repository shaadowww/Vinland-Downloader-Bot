import logging

from aiogram import Bot, Dispatcher, Router , F
from aiogram.types import Message 
from aiogram.filters import Command
from handlers import router
import asyncio

from backend import FakeDownloader

from dotenv import load_dotenv
import os


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
downloader = FakeDownloader(workers=3, queue_size=2)

dp.include_router(router)
async def main():
    asyncio.create_task(downloader.start_workers())
    await dp.start_polling(bot, downloader=downloader)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")