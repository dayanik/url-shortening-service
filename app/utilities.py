import string
import random

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ShortUrlModel
from .settings import get_session


async def get_short_url_entity(session: AsyncSession, short_url: str):
    result = await session.execute(
        select(ShortUrlModel).where(ShortUrlModel.short_code==short_url)
    )
    short_url_entity = result.scalar_one_or_none()
    if short_url_entity is None:
        raise HTTPException(status_code=404, detail="short url not found")
    return short_url_entity


def generate_short_string(length: int=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


async def store_to_db(short_url: str, long_url: str):
    async with get_session() as session:
        try:
            new_short_url = ShortUrlModel(url=long_url, short_code=short_url)
            session.add(new_short_url)
            await session.flush()
            await session.refresh(new_short_url)
            return new_short_url
        except IntegrityError:
            return None
