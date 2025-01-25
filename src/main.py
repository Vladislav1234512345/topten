import sys
import os

from starlette.staticfiles import StaticFiles

from src.container import BASE_DIR

sys.path.insert(1, os.path.join(sys.path[0], ".."))


from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
import uvicorn
from v1 import router as v1_router
from src.database import create_db_and_tables
from src.config import web_settings
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_db_and_tables()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=v1_router)

if not os.path.exists(BASE_DIR / "media"):
    os.mkdir(BASE_DIR / "media")

app.mount(path="/media", app=StaticFiles(directory=BASE_DIR / "media"), name="media")

cors_allowed_origins: list[str] = web_settings.CORS_ALLOWED_ORIGINS.split(";")


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,
    allow_headers=["*"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_credentials=True,
    expose_headers=[
        "Authorization",
        "Origin",
        "X-Requested-With",
        "Content-Type",
        "Accept",
    ],
)


if __name__ == "__main__":
    uvicorn.run(app=app, host=web_settings.WEBAPP_HOST, port=web_settings.WEBAPP_PORT)
