from fastapi import HTTPException, status

from logging_config import error_logger


def database_exception(error: Exception | None = None):
    if error:
        error_logger.error(
            f"Database Error: {error}"
        )
    else:
        error_logger.error(
            "Database Error"
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database Error"
    )


def not_found_exception(name: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{name} not found"
    )


def unauthorized_exception(message: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message
    )


def bad_request_exception(message: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )