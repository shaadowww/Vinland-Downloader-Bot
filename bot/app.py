import logging

import asyncio

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import FSInputFile, TelegramObject

from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import UserCreate, UserUpdate
from database.db_engines import sessionmaker, engine
from database.core import set_user_active_status, upsert_user

from config import settings

from bot.backend import FakeDownloader

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
router = Router()
downloader = FakeDownloader(workers=3, queue_size=10)

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: Any):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        async with self.session_pool() as session:
            data["session"] = session 
            return await handler(event, data)


# Registrate middleware for all text messages
router.message.middleware(DbSessionMiddleware(sessionmaker))


@router.message(Command('start'))
async def send_welcome(message: Message, session: AsyncSession):
    """
    Welcome message on `/start`
    """
    user = UserCreate(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    res = await upsert_user(session, user)
    logging.info(f"Upsert result: {res}")

    await message.answer("Hi!\nI'm vinland downloader bot.")

@router.message(Command('help'))
async def send_help(msg: Message):
    """
    Help message on `/help`
    """
    help_text = (
        "<b>🏴‍☠️ Vinland Downloader Bot — Help Menu</b>\n\n"
        "I'll help you to download video and audio from supported platforms (YouTube, SoundCloud).\n\n"
        "<b>How to use it:</b>\n"
        "Simply send a direct link to a video or audio track. In a few moments  I'll send your ready video !\n\n"
        "<b>Available Commands:</b>\n"
        "• /settings — Configure your default download quality (360p, 720p, 1080p).\n"
        "• /help — Show this help menu.\n\n"
        "<i>If the bot doesn't react to a link, please make sure the URL format is correct.</i>"
    )

    await msg.answer(help_text, parse_mode="HTML")


@router.message(Command('settings'))
async def settings_setup(msg: Message, session: AsyncSession):
    pass

@router.message(Command('run'))
async def bot_get_results(message: Message, session: AsyncSession):
    """
    Get results per user id
    """
    try:
        userid = message.from_user.id
        await message.answer(f"Starting downloads...")
        
        results = await downloader.get_result(userid)

        await message.answer(f"Results: {results}")
        video = FSInputFile(results[0])

        await message.answer_video(video)
    except TelegramForbiddenError:
        await set_user_active_status(session, userid, False)


@router.message()
async def bot_add_task(message: Message, session: AsyncSession):
    try:
        await downloader.add_url(
            message.text,
            message.from_user.id
        )
        await message.answer(f"URL added!")
    except TelegramForbiddenError:
        await set_user_active_status(session, message.from_user.id, False)


dp.include_router(router)

async def main():
    asyncio.create_task(downloader.start_workers())
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Basic startup function
    asyncio.run(main())