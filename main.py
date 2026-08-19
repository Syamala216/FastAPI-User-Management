from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import models

from auth import router as auth_router
from routers.tasks import router as task_router
from routers.users import router as user_router
from routers.products import router as product_router
from routers.wishlist import router as wishlist_router
from routers.cart import router as cart_router
from routers.transactions import router as transaction_router
from routers.admin import router as admin_router


app = FastAPI(
    title="Task Management API"
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("GENERAL ERROR:", exc)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error"
        }
    )


app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(wishlist_router)
app.include_router(cart_router)
app.include_router(transaction_router)
app.include_router(admin_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Task Management API"
    }