# SQLAlchemy Models File


from sqlalchemy import BigInteger, Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column
from database.db_engines import Base
from datetime import datetime
from enum import Enum

class VideoQuality(str, Enum):
    '''
    `User Prefer Enum`
    '''
    P360 = "360p"
    P480 = "480p"
    P720 = "720p"
    P1080 = "1080p"
    ASK = "ask"

class Users(Base):
    '''
    ### Main User Table storing data about users
    '''

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True
    )

    username: Mapped[str | None] = mapped_column(
        String(32)
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE ('utc', now())"),
        onupdate=text("TIMEZONE ('utc', now())")
    )

    download_quality: Mapped[VideoQuality] = mapped_column(
        String(10),
        default=VideoQuality.ASK,
        server_default=text("'ask'")
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        server_default=text("true")
    )

    language_code: Mapped[str | None] = mapped_column(String(10))