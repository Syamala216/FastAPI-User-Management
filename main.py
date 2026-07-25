from fastapi import FastAPI

import models

from database import engine, Base

from auth import router as auth_router
from routers.tasks import router as task_router
from routers.users import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API"
)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)


@app.get("/")
def home():
    return {"message": "Welcome to Task Management API"}