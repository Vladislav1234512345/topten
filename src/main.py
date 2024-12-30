from contextlib import asynccontextmanager

from typing import AsyncGenerator
from fastapi import FastAPI
import uvicorn
from v1 import router as v1_router
from database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_db_and_tables()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=v1_router)


if __name__ == '__main__':
    uvicorn.run(app=app, host='localhost', port=8000)