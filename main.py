from fastapi import FastAPI
import uvicorn
from api import router as api_router

app = FastAPI()

app.include_router(router=api_router)

if __name__ == '__main__':
    uvicorn.run(app=app, host='localhost', port=8000)