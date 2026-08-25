from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError

from logging_config import info_logger

from models.user import User
import schemas
from oauth2 import get_current_user
from exceptions import database_exception


CurrentUser = Annotated[
    User,
    Depends(get_current_user)
]


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# GET CURRENT USER
@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_me(
    current_user: CurrentUser
):
    try:
        # Log user profile access
        info_logger.info(
            f"User ID: {current_user.id} - "
            f"Accessed own profile"
        )

        return current_user

    except SQLAlchemyError as e:
        database_exception(e)