from aiogram.filters.callback_data import CallbackData

class QualityCallback(CallbackData, prefix="set_quality"):
    '''
    Set the quality callback
    '''
    quality: str # 360p 480p 720p 1080p or ask


