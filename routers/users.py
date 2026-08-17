from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError

from models.user import User
import schemas
from oauth2 import get_current_user
from exceptions import database_exception


# Reusable dependency type
CurrentUser = Annotated[User, Depends(get_current_user)]


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_me(
    current_user: CurrentUser
):
    try:
        return current_user

    except SQLAlchemyError:
        database_exception()