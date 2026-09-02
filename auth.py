import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from logging_config import info_logger, warning_logger

from models.user import User
import schemas
from database import get_db
from hashing import Hash
from oauth2 import create_access_token
from exceptions import database_exception
from email_service import send_otp_email


DbSession = Annotated[
    Session,
    Depends(get_db)
]

OAuth2Form = Annotated[
    OAuth2PasswordRequestForm,
    Depends()
]


router = APIRouter(
    tags=["Authentication"]
)


# ==========================================================
# OTP GENERATION
# ==========================================================

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


# ==========================================================
# REGISTER
# ==========================================================

@router.post(
    "/register",
    response_model=schemas.UserResponse
)
def register(
    user: schemas.UserCreate,
    db: DbSession
):
    try:

        # Check username
        existing_username = db.query(User).filter(
            User.username == user.username
        ).first()

        if existing_username:
            warning_logger.warning(
                f"Registration failed - "
                f"Username already exists - "
                f"Username: {user.username}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check email
        existing_email = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing_email:
            warning_logger.warning(
                f"Registration failed - "
                f"Email already exists - "
                f"Email: {user.email}"
            )

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

        # Log successful registration
        info_logger.info(
            f"User ID: {new_user.id} - "
            f"User registered successfully - "
            f"Username: {new_user.username}"
        )

        return new_user

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# ==========================================================
# LOGIN
# ==========================================================

@router.post(
    "/login",
    response_model=schemas.Token
)
def login(
    request: OAuth2Form,
    db: DbSession
):
    try:

        # Find user by email
        db_user = db.query(User).filter(
            User.email == request.username
        ).first()

        if not db_user:
            warning_logger.warning(
                f"Login failed - "
                f"Invalid email - "
                f"Email: {request.username}"
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid Email"
            )

        # Verify password
        if not Hash.verify(
            request.password,
            db_user.password
        ):
            warning_logger.warning(
                f"Login failed - "
                f"Invalid password - "
                f"User ID: {db_user.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Password"
            )

        # Create JWT token
        access_token = create_access_token(
            data={"user_id": db_user.id},
            expires_delta=timedelta(minutes=30)
        )

        # Log successful login
        info_logger.info(
            f"User ID: {db_user.id} - "
            f"Login successful"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)

# ==========================================================
# FORGOT PASSWORD
# ==========================================================

@router.post("/forgot-password")
def forgot_password(
    data: schemas.ForgotPassword,
    db: DbSession
):
    try:

        # Find user by email
        db_user = db.query(User).filter(
            User.email == data.email
        ).first()

        if not db_user:
            warning_logger.warning(
                f"Forgot password failed - "
                f"Email not found - "
                f"Email: {data.email}"
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )

        # Generate OTP
        otp = generate_otp()

        # OTP valid for 5 minutes
        otp_expiry = (
            datetime.now(timezone.utc)
            + timedelta(minutes=5)
        )

        # Send OTP through Gmail SMTP
        try:
            send_otp_email(
                receiver_email=db_user.email,
                username=db_user.username,
                otp=otp
            )

        except smtplib.SMTPException as e:
            warning_logger.warning(
                f"OTP email failed - "
                f"Email: {db_user.email} - "
                f"Error: {e}"
            )

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to send OTP email. Please try again later"
            )

        # Save OTP only after email is sent successfully
        db_user.otp = otp
        db_user.otp_expiry = otp_expiry

        db.commit()

        # Log successful OTP request
        info_logger.info(
            f"User ID: {db_user.id} - "
            f"Forgot password OTP sent"
        )

        return {
            "message": "OTP sent successfully to your email"
        }

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)
# ==========================================================
# VERIFY OTP
# ==========================================================

@router.post("/verify-otp")
def verify_otp(
    data: schemas.VerifyOTP,
    db: DbSession
):
    try:

        # Find user by email
        db_user = db.query(User).filter(
            User.email == data.email
        ).first()

        if not db_user:
            warning_logger.warning(
                f"OTP verification failed - "
                f"Email not found - "
                f"Email: {data.email}"
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )

        # Check whether OTP exists
        if not db_user.otp:
            warning_logger.warning(
                f"OTP verification failed - "
                f"No OTP found - "
                f"User ID: {db_user.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not found. Please request a new OTP"
            )

        # Check OTP
        if db_user.otp != data.otp:
            warning_logger.warning(
                f"OTP verification failed - "
                f"Invalid OTP - "
                f"User ID: {db_user.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )

        # Check OTP expiry
        if (
            not db_user.otp_expiry
            or datetime.now() > db_user.otp_expiry
        ):
            warning_logger.warning(
                f"OTP verification failed - "
                f"OTP expired - "
                f"User ID: {db_user.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired. Please request a new OTP"
            )

        # OTP is valid
        info_logger.info(
            f"User ID: {db_user.id} - "
            f"OTP verified successfully"
        )

        return {
            "message": "OTP verified successfully"
        }

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)



# RESET PASSWORD


@router.post("/reset-password")
def reset_password(
    data: schemas.ResetPassword,
    db: DbSession
):
    try:

        # Find user by email
        db_user = db.query(User).filter(
            User.email == data.email
        ).first()

        if not db_user:
            warning_logger.warning(
                f"Password reset failed - "
                f"Email not found - "
                f"Email: {data.email}"
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )

        # Check OTP exists
        if not db_user.otp:
            warning_logger.warning(
                f"Password reset failed - "
                f"No OTP found - "
                f"User ID: {db_user.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not found. Please request a new OTP"
            )

        # Check OTP
        if db_user.otp != data.otp:
            warning_logger.warning(
                f"Password reset failed - "
                f"Invalid OTP - "
                f"User ID: {db_user.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )

        # Check OTP expiry
        if (
            not db_user.otp_expiry
            or datetime.now() > db_user.otp_expiry
        ):
            warning_logger.warning(
                f"Password reset failed - "
                f"OTP expired - "
                f"User ID: {db_user.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired. Please request a new OTP"
            )

        # Hash new password
        hashed_password = Hash.bcrypt(
            data.new_password
        )

        # Update password
        db_user.password = hashed_password

        # Clear OTP after successful reset
        db_user.otp = None
        db_user.otp_expiry = None

        db.commit()

        # Log successful password reset
        info_logger.info(
            f"User ID: {db_user.id} - "
            f"Password reset successfully"
        )

        return {
            "message": "Password reset successfully"
        }

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)