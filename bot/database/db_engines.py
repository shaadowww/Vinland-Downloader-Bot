# Technical Part

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from bot.config import settings

engine = create_async_engine(
    settings.DB_URL
)

sessionmaker = async_sessionmaker(engine, expire_on_commit=False) 

class Base(DeclarativeBase):
    ...