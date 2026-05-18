# Validation Schemas

from datetime import datetime
from enum import Enum
from pydantic import ConfigDict

from pydantic import BaseModel, Field

class VideoQuality(str, Enum):
    P480 = "480p"
    P720 = "720p"
    P1080 = "1080p"
    ASK = "ask"

class UserBase(BaseModel):
    
    telegram_id: int
    username: str | None = Field(default=None, ge=1, le=32)
    download_quality: VideoQuality = Field(default=VideoQuality.ASK)
    language_code: str | None = Field(default=None, max_length=10)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    
    username: str | None = Field(default=None, max_length=32)
    download_quality: VideoQuality | None = Field(default=None)
    is_active: bool | None = Field(default=None)
    language_code: str | None = Field(default=None, max_length=10)

class UserRead(UserBase):
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)