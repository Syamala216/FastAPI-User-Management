from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class PasswordResetOTP(Base):

    __tablename__ = "password_reset_otps"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    otp = Column(
        String,
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    user = relationship(
        "User"
    )