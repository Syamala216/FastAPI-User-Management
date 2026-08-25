from fastapi import APIRouter, Query
from sqlalchemy.exc import SQLAlchemyError

from logging_config import info_logger

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

        # Log successful admin action
        info_logger.info(
            f"Admin ID: {current_admin.id} - "
            f"Viewed users - "
            f"Page: {page} - "
            f"Limit: {limit}"
        )

        return users

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


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

        # Log successful admin action
        info_logger.info(
            f"Admin ID: {current_admin.id} - "
            f"Viewed products - "
            f"Page: {page} - "
            f"Limit: {limit}"
        )

        return products

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)