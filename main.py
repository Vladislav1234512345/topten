from contextlib import asynccontextmanager

from typing import AsyncGenerator
from fastapi import FastAPI
import uvicorn
from api import router as api_router
from database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    await create_db_and_tables()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=api_router)


if __name__ == '__main__':
    uvicorn.run(app=app, host='localhost', port=8000)