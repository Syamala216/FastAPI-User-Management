import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        description="Username must be between 3 and 30 characters"
    )

    email: EmailStr

    password: str

    is_admin: bool = False

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if len(value) < 8:
            raise ValueError("Password must contain at least 8 characters")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")

        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=100,
        description="Task title"
    )

    description: Optional[str] = None

    completed: bool = False



class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    owner_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None

class ProductCreate(BaseModel):
    name: str
    description:Optional[str]
    price: float
    stock: int
    category: str


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: str
    owner_id: int

    class Config:
        from_attributes = True


class WishlistCreate(BaseModel):
    product_id: int


class ProductWishlist(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    category: str

    class Config:
        from_attributes = True


class WishlistResponse(BaseModel):
    id: int
    user_id: int
    product: ProductWishlist

    class Config:
        from_attributes = True

class CartCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartResponse(BaseModel):
    id: int
    user_id: int
    product_name: str
    quantity: int

class TransactionCreate(BaseModel):
    product_id: int
    quantity: int
    payment_status: str


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_amount: float
    payment_status: str

    class Config:
        from_attributes = True