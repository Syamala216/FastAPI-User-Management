from fastapi import HTTPException, status


def database_exception():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database Error"
    )