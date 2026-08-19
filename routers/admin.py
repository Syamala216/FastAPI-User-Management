from fastapi import APIRouter

from models.user import User
from models.product import Product

from oauth2 import CurrentAdmin, DbSession


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# GET ALL USERS - ADMIN ONLY
@router.get("/users")
def get_all_users(
    current_admin: CurrentAdmin,
    db: DbSession,
    page: int = 1,
    limit: int = 10
):
    offset = (page - 1) * limit

    users = (
        db.query(User)
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


# GET ALL PRODUCTS - ADMIN ONLY
@router.get("/products")
def get_all_products(
    current_admin: CurrentAdmin,
    db: DbSession,
    page: int = 1,
    limit: int = 10
):
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