from fastapi import APIRouter, Query
from sqlalchemy.exc import SQLAlchemyError

import schemas
from models.user import User
from models.product import Product
from oauth2 import DbSession, CurrentAdmin
from exceptions import database_exception


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# GET ALL USERS
@router.get(
    "/users",
    response_model=list[schemas.UserResponse]
)
def get_all_users(
    db: DbSession,
    current_admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
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

        return users

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# GET ALL PRODUCTS
@router.get(
    "/products",
    response_model=list[schemas.ProductResponse]
)
def get_all_products(
    db: DbSession,
    current_admin: CurrentAdmin,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
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

        return products

    except SQLAlchemyError:
        db.rollback()
        database_exception()