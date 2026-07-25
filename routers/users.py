from fastapi import APIRouter, Depends

import models
import schemas
from oauth2 import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Get currently logged-in user.
    """
    return current_user