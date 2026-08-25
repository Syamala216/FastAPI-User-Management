import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import models

from logging_config import (
    info_logger,
    warning_logger,
    error_logger
)

from oauth2 import get_user_id_from_token

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


# REQUEST LOGGING MIDDLEWARE
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Get Authorization header
    authorization = request.headers.get("Authorization")

    # Default for requests without login
    user_id = None

    # Get user ID from JWT token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user_id = get_user_id_from_token(token)

    try:
        response = await call_next(request)

        process_time = time.time() - start_time

        # WARNING logs for unsuccessful requests
        if response.status_code >= 400:
            warning_logger.warning(
                f"User ID: {user_id} - "
                f"{request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.4f}s"
            )

        # INFO logs for successful requests
        else:
            info_logger.info(
                f"User ID: {user_id} - "
                f"{request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.4f}s"
            )

        return response

    # ERROR logs for unexpected exceptions
    except Exception as exc:
        process_time = time.time() - start_time

        error_logger.error(
            f"User ID: {user_id} - "
            f"{request.method} {request.url.path} "
            f"Error: {exc} "
            f"Time: {process_time:.4f}s"
        )

        raise


# GLOBAL EXCEPTION HANDLER
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    error_logger.error(
        f"{request.method} {request.url.path} "
        f"GENERAL ERROR: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error"
        }
    )


# INCLUDE ROUTERS
app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(wishlist_router)
app.include_router(cart_router)
app.include_router(transaction_router)
app.include_router(admin_router)


# HOME
@app.get("/")
def home():
    return {
        "message": "Welcome to Task Management API"
    }
"""@app.get("/test-error")
def test_error():
    raise Exception("This is a test error")"""