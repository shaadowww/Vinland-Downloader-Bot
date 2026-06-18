import logging
import redis.asyncio as redis
from json import dumps

from typing import Any, Awaitable, Callable, Dict

from aiogram import Router , F, BaseMiddleware
from aiogram.types import Message , CallbackQuery
from aiogram.filters import Command
<<<<<<< HEAD
=======
import keyboards as kb
>>>>>>> f719ee3befdef96dfbfb804bb22e6e377c466dc2

from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.types import FSInputFile, TelegramObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sqlalchemy.ext.asyncio import AsyncSession

from database.schemas import UserCreate, UserUpdate
from database.db_engines import sessionmaker
from database.core import set_user_active_status, update_user, upsert_user

<<<<<<< HEAD
from bot.backend import FakeDownloader
import bot.keyboards as kb

valid_url_regex = os.getenv('VALID_URL_REGEX')
invalid_url_regex = os.getenv('INVALID_URl_REGEX')
=======
valid_url_regex = r'(?<!\S)https://(?:www\.)?(?:[a-zA-Z0-9-]+\.)?(?:youtube\.com|youtu\.be|soundcloud\.com|on\.soundcloud\.com)\S+'
invalid_url_regex = r'^https://(?!(www\.)?([a-zA-Z0-9-]+\.)?(youtube\.com|youtu\.be|soundcloud\.com|on\.soundcloud\.com))\S+'
>>>>>>> f719ee3befdef96dfbfb804bb22e6e377c466dc2
router = Router()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)

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

    await message.answer(
<<<<<<< HEAD
        text="<b>Hi!\nI'm Vinland downloader bot.n\n🏞️ I'll help you to download video/music from Youtube/Soundcloud</b>",
        parse_mode="HTML",
        reply_markup=kb.work
=======
        text="<b>Hi!\nI'm vinland downloader bot.\n🏞️ I'll help you to download video/music from Youtube/Soundcloud</b>",
        parse_mode="HTML"
>>>>>>> f719ee3befdef96dfbfb804bb22e6e377c466dc2
        )
    

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
async def show_settings(msg: Message):
    '''
    Displays configuration menu `/settings`
    '''

    builder = InlineKeyboardBuilder()

    for q in ["360p", "480p", "720p", "1080p"]:
        builder.button(text=q, callback_data=kb.QualityCallback(quality=q))
        builder.button(text="Audio", callback_data=kb.FormatCallback(format="audio"))
        builder.button(text="Video", callback_data=kb.FormatCallback(format="video"))
        builder.button(text="Always Ask", callback_data=kb.QualityCallback(quality="ask"))

        builder.adjust(4, 2, 1)

        await msg.answer(
            text="<b>⚙️ Settings</b>\n\nSelect your default video download quality:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )


@router.callback_query(kb.QualityCallback.filter())
async def quality_selection_callback(
    callback: CallbackQuery,
    callback_data: kb.QualityCallback,
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

    readable_quality = "Always ask" if callback_data.quality == "ask" else callback_data.quality
    await callback.message.edit_text(
        text=f"<b> ✓ Settings Saved</b>\n\nDefault download quality updated to: <b>{readable_quality}</b>",
        parse_mode="HTML"
    )

@router.callback_query(kb.FormatCallback.filter())
async def format_selection_callback(
    callback: CallbackQuery,
    callback_data: kb.FormatCallback,
    session: AsyncSession
    ):
    '''
    Processing format callback selection
    '''
    telegram_id = callback.from_user.id
    selected_format = UserUpdate(
        download_format=callback.data.format 
    )
    
    await update_user(session, telegram_id, selected_format)
    await callback.answer(text=f"format set to {callback_data.format}")
    
    await callback.message.edit_text(
        text=f"<b> ✓ Settings Saved</b>\n\nDefault format updated to: <b>{callback_data.format.upper()}</b>",
        parse_mode="HTML"
    )
# TODO
# add animation to waiting message...
# choose format via buttons

@router.message(F.text.regexp(valid_url_regex))
async def bot_add_task(message: Message):
    await message.answer("Working on it...")
    await queue_add(
        message.chat.id,
        message.text,
        quality = 720,
        format = "audio"
        )
    
# cancel downloads
@router.message(Command('cancel'))
async def cancel_task(message: Message):
    logging.info("cancel command")
    ...

# REDIS
async def queue_add(chat_id: int, url: str, quality: int, format: str):
    # try:
    async with redis.Redis(
        host='redis', port=6379, decode_responses=True
    ) as r:
        await r.lpush(
            'download_queue',
            dumps({
                "chat_id": chat_id, 
                "url": url,
                "quality": quality,
                "format": format
                })
            )
    #     await message.answer(f"URL added!")
    # except TelegramForbiddenError:
    # TODO
    # переписать user.id на chat_id так как тут анриал получить userid, по-моему
    #     await set_user_active_status(session, message.from_user.id, False)

@router.message(F.text.regexp(invalid_url_regex)) 
async def bad_url(message: Message): 
    await message.answer("Bad URL")

# @router.message()
# async def message(message: Message): 
#     await message.answer("Dont spam, i ignore u")

