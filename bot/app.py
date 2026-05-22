import logging

import asyncio

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot, Dispatcher, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.types import FSInputFile, TelegramObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.keyboards import QualityCallback

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Users
from database.schemas import UserCreate, UserUpdate
from database.db_engines import sessionmaker, engine
from database.core import set_user_active_status, update_user, upsert_user

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
router.callback_query.middleware(DbSessionMiddleware(sessionmaker))


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
        "🌊 Simply send a direct link to a video or audio track. In a few moments  I'll send your ready video !\n\n"
        "<b>🌌 Available Commands:</b>\n"
        "🌀 /settings — Configure your default download quality (360p, 720p, 1080p).\n"
        "🌀 /help — Show this help menu.\n\n"
        "<i>If the bot doesn't react to a link, please make sure the URL format is correct.</i>"
    )

    await msg.answer(help_text, parse_mode="HTML")


@router.message(Command('settings'))
async def show_settings(msg: Message, session: AsyncSession):
    '''
    Displays configuration menu `/settings`
    '''

    builder = InlineKeyboardBuilder()

    builder.button(text="360p", callback_data=QualityCallback(quality="360p"))
    builder.button(text="480p", callback_data=QualityCallback(quality="480p"))
    builder.button(text="720p", callback_data=QualityCallback(quality="720p"))
    builder.button(text="1080p", callback_data=QualityCallback(quality="1080p"))
    builder.button(text="Always Ask", callback_data=QualityCallback(quality="ask"))

    builder.adjust(4, 1)

    await msg.answer(
        text="<b>⚙️ Settings</b>\n\nSelect your default video download quality:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(QualityCallback.filter())
async def quaity_selection_callback(
    callback: CallbackQuery,
    callback_data: QualityCallback,
    session: AsyncSession
):
    '''
    Processing quality callback selection
    '''

    telegram_id = callback.from_user.id
    selected_quality = UserUpdate(
        download_quality=callback_data.quality
    )

    await update_user(session, telegram_id, selected_quality)

    await callback.answer(
        text=f"Quality set to {callback_data.quality}"
    )

    readable_quality = "Always ask " if callback_data.quality == "ask" else callback_data.quality
    await callback.message.edit_text(
        text=f"<b> ✓ Settings Saved</b>\n\nDefault download quality updated to: <b>{readable_quality}</b>",
        parse_mode="HTML"
    )

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