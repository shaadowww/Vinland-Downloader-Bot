from dotenv import load_dotenv
import os
import logging

from typing import Any, Awaitable, Callable, Dict

from aiogram import Router , F, BaseMiddleware
from aiogram.types import Message , CallbackQuery
from aiogram.filters import Command
import bot.keyboards as kb

from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.types import FSInputFile, TelegramObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

# from sqlalchemy.ext.asyncio import AsyncSession

# from database.schemas import UserCreate, UserUpdate
# from database.db_engines import sessionmaker
# from database.core import set_user_active_status, update_user, upsert_user

from backend import FakeDownloader

# valid_url_regex = os.getenv('VALID_URL_REGEX')
# invalid_url_regex = os.getenv('INVALID_URl_REGEX')
router = Router()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)

# class DbSessionMiddleware(BaseMiddleware):
#     def __init__(self, session_pool: Any):
#         super().__init__()
#         self.session_pool = session_pool

#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: Dict[str, Any]
#     ) -> Any:
        
#         async with self.session_pool() as session:
#             data["session"] = session 
#             return await handler(event, data)

# Registrate middleware for all text messages
# router.message.middleware(DbSessionMiddleware(sessionmaker))
# router.callback_query.middleware(DbSessionMiddleware(sessionmaker))
    

@router.message(Command('start'))
async def send_welcome(message: Message):
    """
    Welcome message on `/start`
    """
    # user = UserCreate(
    #     telegram_id=message.from_user.id,
    #     username=message.from_user.username
    # )
    # res = await upsert_user(session, user)
    # logging.info(f"Upsert result: {res}")

    await message.answer(
        text="<b>Hi!\nI'm vinland downloader bot.\n🏞️ I'll help you to download video/music from Youtube/Soundcloud</b>",
        parse_mode="HTML",
        reply_markup=kb.work
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


# @router.message(Command('settings'))
# async def show_settings(msg: Message):
#     '''
#     Displays configuration menu `/settings`
#     '''

#     builder = InlineKeyboardBuilder()

#     builder.button(text="360p", callback_data=kb.QualityCallback(quality="360p"))
#     builder.button(text="480p", callback_data=kb.QualityCallback(quality="480p"))
#     builder.button(text="720p", callback_data=kb.QualityCallback(quality="720p"))
#     builder.button(text="1080p", callback_data=kb.QualityCallback(quality="1080p"))
#     builder.button(text="Always Ask", callback_data=kb.QualityCallback(quality="ask"))

#     builder.adjust(4, 1)

#     await msg.answer(
#         text="<b>⚙️ Settings</b>\n\nSelect your default video download quality:",
#         reply_markup=builder.as_markup(),
#         parse_mode="HTML"
#     )


# @router.callback_query(kb.QualityCallback.filter())
# async def quality_selection_callback(
#     callback: CallbackQuery,
#     callback_data: kb.QualityCallback,
#     session: AsyncSession
# ):
#     '''
#     Processing quality callback selection
#     '''

#     telegram_id = callback.from_user.id
#     selected_quality = UserUpdate(
#         download_quality=callback_data.quality
#     )

#     await update_user(session, telegram_id, selected_quality)

#     await callback.answer(
#         text=f"Quality set to {callback_data.quality}"
#     )

#     readable_quality = "Always ask" if callback_data.quality == "ask" else callback_data.quality
#     await callback.message.edit_text(
#         text=f"<b> ✓ Settings Saved</b>\n\nDefault download quality updated to: <b>{readable_quality}</b>",
#         parse_mode="HTML"
#     )


# @router.message(F.data == "Run")
# @router.message(Command('run'))
async def bot_get_results(message: Message, downloader: FakeDownloader):
    """
    Get results per user id
    """
    # try:
    userid = message.from_user.id
    await message.answer(f"Starting downloads...")
    
    results = await downloader.get_result(userid)
    if len(results) < 1:
        await message.answer("Invalid url")
    else:
        file_path = results[0]
    if not os.path.exists(file_path):
        logging.error(f"Invalid path {file_path}")
        return None

    try:
        logging.debug(f"userid{userid} | download results: {results}")
        video = FSInputFile(file_path)
        await message.answer_video(video)
    finally:
        os.remove(file_path)
    # except TelegramForbiddenError:
    #     await set_user_active_status(session, userid, False)


@router.message()
async def bot_add_task(message: Message, downloader: FakeDownloader):
    # try:
    await downloader.add_url(
        message.text,
        message.from_user.id
    )
    await bot_get_results(message, downloader)
    # await message.answer(f"URL added!")
    # except TelegramForbiddenError:
    #     await set_user_active_status(session, message.from_user.id, False)


# @router.message(F.text.regexp(invalid_url_regex)) 
# async def bad_url(message: Message): 
#     await message.answer("Bad URL")

# @router.message()
# async def message(message: Message): 
#     await message.answer("Dont spam, i ignore u")

