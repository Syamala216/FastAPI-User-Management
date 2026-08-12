from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import schemas
from database import get_db
from models.user import User
from models.product import Product
from models.wishlist import Wishlist
from oauth2 import get_current_user
from exceptions import database_exception



db_dependency = Depends(get_db)
user_dependency = Depends(get_current_user)


router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)


# ADD TO WISHLIST
@router.post(
    "/",
    response_model=schemas.WishlistResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_wishlist(
    wishlist: schemas.WishlistCreate,
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:

        # Check product exists
        product = db.query(Product).filter(
            Product.id == wishlist.product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # User cannot add own product
        if product.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add your own product to wishlist"
            )

        # Check already exists
        existing = db.query(Wishlist).filter(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == wishlist.product_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product already in wishlist"
            )

        # Create wishlist
        new_wishlist = Wishlist(
            user_id=current_user.id,
            product_id=wishlist.product_id
        )

        db.add(new_wishlist)
        db.commit()
        db.refresh(new_wishlist)

        return {
            "id": new_wishlist.id,
            "user_id": new_wishlist.user_id,
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "category": product.category
            }
        }

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# GET WISHLIST
@router.get(
    "/",
    response_model=list[schemas.WishlistResponse]
)
def get_wishlist(
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:

        wishlist_items = (
            db.query(Wishlist, Product)
            .join(
                Product,
                Wishlist.product_id == Product.id
            )
            .filter(
                Wishlist.user_id == current_user.id
            )
            .all()
        )

        result = []

        for wishlist, product in wishlist_items:

            result.append({
                "id": wishlist.id,
                "user_id": wishlist.user_id,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock,
                    "category": product.category
                }
            })

        return result

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# REMOVE FROM WISHLIST
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
def remove_from_wishlist(
    product_id: int,
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:

        wishlist = db.query(Wishlist).filter(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == product_id
        ).first()

        if wishlist is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in wishlist"
            )

        db.delete(wishlist)
        db.commit()

        return {
            "message": "Product removed from wishlist successfully"
        }

    except SQLAlchemyError:
        db.rollback()
        database_exception()