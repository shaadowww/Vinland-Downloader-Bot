import logging

from aiogram import Bot, Dispatcher, Router , F
from aiogram.types import Message 
from aiogram.filters import Command
import asyncio

from dotenv import load_dotenv
import os

from backend import FakeDownloader

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
downloader = FakeDownloader(workers=3, queue_size=2)
valid_url_regex = os.getenv('VALID_URL_REGEX')
invalid_url_regex = os.getenv('INVALID_URl_REGEX')

@router.message(Command('start'))
async def send_welcome(message: Message):
    """
    Hello message on `/start` or `/help` command
    """
    await message.answer("Hi!\nI'm vinland downloader bot.")

@router.message(Command('run'))
async def bot_get_results(message: Message):
    """
    Get results per user id
    """

    await message.answer(f"Starting downloads...")
    
    results = await downloader.get_result(message.from_user.id)

    await message.answer(f"Results: {results}")


@router.message(F.text.regexp(valid_url_regex))
async def bot_add_task(message: Message):
    await downloader.add_url(message.text, message.from_user.id)
    
    await message.answer(f"URL added!")

@router.message(F.text.regexp(invalid_url_regex)) 
async def bad_url(message: Message): 
    await message.answer("Bad URL")

@router.message()
async def message(message: Message): 
    await message.answer("Dont spam, i ignore u")
dp.include_router(router)

async def main():
    asyncio.create_task(downloader.start_workers())
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Basic startup function
    asyncio.run(main())