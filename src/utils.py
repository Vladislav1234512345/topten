from fastapi import HTTPException
from sqlmodel import SQLModel, select

from database import AsyncSessionDep
from exceptions import invalid_email_exception


async def insert_instance(instance: SQLModel, session: AsyncSessionDep, exception: HTTPException) -> SQLModel:
    session.add(instance)
    try:
        await session.commit()
    except Exception:
        raise exception
    await session.refresh(instance)

    return instance


async def select_instance(cls, session: AsyncSessionDep, **filters) -> SQLModel:
    statement = select(cls).filter_by(**filters)
    try:
        result = await session.execute(statement)
    except:
        raise invalid_email_exception
    user = result.scalar()

    return user

