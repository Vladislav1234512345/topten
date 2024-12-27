from fastapi import HTTPException

from models import Base
from database import AsyncSessionDep



async def create_db_table_instance(instance: Base, session: AsyncSessionDep, exception: HTTPException) -> Base:
    session.add(instance)
    try:
        await session.commit()
    except Exception:
        raise exception
    await session.refresh(instance)

    return instance

