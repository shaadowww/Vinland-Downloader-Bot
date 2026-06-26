# Database Query Functions; CRUD

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import Users
from bot.database.schemas import UserCreate, UserRead, UserUpdate
from typing import Optional, List

async def upsert_user(session: AsyncSession, user_schema: UserCreate) -> UserRead:
    """
    `DATABASE` \n
    Creates an user or updates an existing user if they have changed their name
    """

    user = await session.get(Users, user_schema.telegram_id)

    if user:
        user.username = user_schema.username
    else: 
        user = Users(**user_schema.model_dump())
        session.add(user)
    
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)

async def get_user(session: AsyncSession, telegram_id: int) -> Optional[UserRead]:
    """
    `DATABASE` \n
    Checks if there's a user and returning it
    """

    user = await session.get(Users, telegram_id)

    return UserRead.model_validate(user) if user else None

async def update_user(
        session: AsyncSession, telegram_id: int, user_schema: UserUpdate
    ) -> Optional[UserRead]:
    """
    `DATABASE` \n
    Updates specific user fields (e.g., `configuration`, `quality preferences`, or `username`)
    """

    user = await session.get(Users, telegram_id)

    if not user:
        return None 

    update_data = user_schema.model_dump(exclude_unset=True)

    for key, val in update_data.items():
        setattr(user, key, val)

    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)

async def delete_user(session: AsyncSession, telegram_id: int) -> bool:
    """
    `DATABASE` \n
    Delete specified user from `Users` Model
    """

    user = await session.get(Users, telegram_id)
 
    if not user:
        return False

    await session.delete(user)
    await session.commit()
    return True


async def set_user_active_status(
        session: AsyncSession, telegram_id: int, is_active: bool
    ) -> bool:
    """
    `DATABASE` \n
    Fast toggle for user active status (used when user blocks/unblocks the bot)
    """

    user = await session.get(Users, telegram_id)

    if user is None:
        return False
    
    user.is_active = is_active

    await session.commit()
    
    return True

async def get_all_active_users(session: AsyncSession) -> List[UserRead]:
    """
    `DATABASE` \n
    Returns a list of all active users for broad notifications 
    """

    query = select(Users).where(Users.is_active == True)

    result = await session.execute(query)
    users = result.scalars().all()

    return [UserRead.model_validate(user) for user in users]
