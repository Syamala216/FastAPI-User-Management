from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    tasks = relationship("Task", back_populates="owner")

    is_admin = Column(Boolean, default=False)
    otp = Column(String, nullable=True)

    otp_expiry = Column(DateTime, nullable=True)