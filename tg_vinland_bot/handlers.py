from dotenv import load_dotenv
import os
from aiogram import Router , F 
from aiogram.types import Message , CallbackQuery
from aiogram.filters import Command , CommandStart 
import keyboards as kb 

from backend import FakeDownloader

load_dotenv()

valid_url_regex = os.getenv('VALID_URL_REGEX')
invalid_url_regex = os.getenv('INVALID_URl_REGEX')
router = Router()

@router.message(CommandStart())
async def send_welcome(message: Message):
    """
    Hello message on `/start` or `/help` command
    """
    await message.answer("Hi!\nI'm vinland downloader bot.\nPlease send me URL", reply_markup=kb.work)

@router.callback_query(F.data == "Run")
async def bot_get_results(callback: CallbackQuery , downloader: FakeDownloader):
    """
    Get results per user id
    """

    await callback.answer(f"Starting downloads...")
    
    results = await downloader.get_result(callback.from_user.id)

    await callback.message.answer(f"Results: {results}")


@router.message(F.text.regexp(valid_url_regex))
async def bot_add_task(message: Message, downloader: FakeDownloader):
    await downloader.add_url(message.text, message.from_user.id)
    
    await message.answer(f"URL added!")

@router.message(F.text.regexp(invalid_url_regex)) 
async def bad_url(message: Message): 
    await message.answer("Bad URL")

@router.message()
async def message(message: Message): 
    await message.answer("Dont spam, i ignore u")


