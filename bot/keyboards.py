from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

class QualityCallback(CallbackData, prefix="set_quality"):
    """Set the quality callback"""

    quality: str # 360p 480p 720p 1080p or ask

class FormatCallback(CallbackData, prefix="set_format"):
    """Set the format for download"""
    
    format: str # audio, video, both

from aiogram.types import  InlineKeyboardMarkup , InlineKeyboardButton

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="start", callback_data="start")]
    ])

def settings_keyboard(current_quality: str, current_format: str) -> InlineKeyboardMarkup:
    """Get settings keyboard"""

    builder = InlineKeyboardBuilder()

    for q in ["360p", "480p", "720p", "1080p"]:
        text = f"✅ {q}" if current_quality == q else q
        builder.button(text=text, callback_data=QualityCallback(quality=q))

    # text variables
    audio_text = "✅ Audio" if current_format == "audio" else "Audio" 
    video_text = "✅ Video" if current_format == "video" else "Video"
    both_text = "✅ Both" if current_format == "both" else "Both"
    ask_text = "✅ Always Ask" if current_quality == "ask" else "Always Ask"


    builder.button(text=audio_text, callback_data=FormatCallback(format="audio"))
    builder.button(text=video_text, callback_data=FormatCallback(format="video"))
    builder.button(text=both_text, callback_data=FormatCallback(format="both"))
    builder.button(text=ask_text, callback_data=QualityCallback(quality="ask"))

    builder.adjust(4, 3, 1)
    return builder.as_markup()