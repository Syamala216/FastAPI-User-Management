from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models.user import User
from models.product import Product
from oauth2 import get_current_admin
from exceptions import database_exception


DbSession = Annotated[Session, Depends(get_db)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# GET ALL USERS - ADMIN ONLY
@router.get("/users")
def get_all_users(
    db: DbSession,
    current_admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1)
):
    try:

        offset = (page - 1) * limit

        users = (
            db.query(User)
            .order_by(User.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
            for user in users
        ]

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# GET ALL PRODUCTS - ADMIN ONLY
@router.get("/products")
def get_all_products(
    db: DbSession,
    current_admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1)
):
    try:

        offset = (page - 1) * limit

        products = (
            db.query(Product)
            .order_by(Product.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "category": product.category,
                "owner_id": product.owner_id
            }
            for product in products
        ]

    except SQLAlchemyError:
        db.rollback()
        database_exception()