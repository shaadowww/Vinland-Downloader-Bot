import logging
import asyncio
import os

from aiogram import Bot, Dispatcher

from handlers import router


# from config import settings
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize bot and dispatcher
# if not settings.BOT_TOKEN:
#     raise ValueError("BOT_TOKEN is missing")

# bot = Bot(token=settings.BOT_TOKEN)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router)

async def main():
    await dp.start_polling(bot)
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.debug("The bot work is stopping...")
