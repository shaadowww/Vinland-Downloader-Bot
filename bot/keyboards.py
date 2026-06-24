from aiogram.filters.callback_data import CallbackData

class QualityCallback(CallbackData, prefix="set_quality"):
    '''
    Set the quality callback
    '''
    quality: str # 360p 480p 720p 1080p or ask

class FormatCallback(CallbackData, prefix="set_format"):
    '''
    Set the format for download
    '''
    format: str # audio, video

from aiogram.types import  InlineKeyboardMarkup , InlineKeyboardButton

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="start", callback_data="start")]
    ])

