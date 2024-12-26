from typing import Optional

from models import Base
from database import AsyncSessionDep
from sqlmodel import select
from api.v1.jwt.exceptions import unauthorized_exception


# async def get_db_table_instance(cls, session: AsyncSessionDep, **data) -> Optional[Base]:
#     statement = select(cls).filter_by(**data)
#     try:
#         result = await session.execute(statement)
#     except:
#         raise unauthorized_exception
#     db_table_instance = result.scalar()
#
#     if not db_table_instance:
#         raise unauthorized_exception
#
#     return db_table_instance


async def create_db_table_instance(instance: Base, session: AsyncSessionDep) -> Base:
    session.add(instance)
    await session.commit()
    await session.refresh(instance)

    return instance