from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.user import User
import schemas
from database import get_db
from hashing import Hash
from oauth2 import create_access_token
from exceptions import database_exception

router = APIRouter(
    tags=["Authentication"]
)


# REGISTER

@router.post("/register", response_model=schemas.UserResponse)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    try:

        # Check username
        existing_username = db.query(User).filter(
            User.username == user.username
        ).first()

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check email
        existing_email = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Hash password
        hashed_password = Hash.bcrypt(user.password)

        # Create user
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            is_admin=user.is_admin
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# LOGIN

@router.post("/login", response_model=schemas.Token)
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        # Find user by email
        db_user = db.query(User).filter(
            User.email == request.username
        ).first()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid Email"
            )

        # Verify password
        if not Hash.verify(request.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Password"
            )

        # Create JWT Token
        access_token = create_access_token(
            data={"user_id": db_user.id},
            expires_delta=timedelta(minutes=30)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except SQLAlchemyError as e:
        db.rollback()
        print("LOGIN DATABASE ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )