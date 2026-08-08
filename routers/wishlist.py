from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
from database import get_db
from models.user import User
from oauth2 import get_current_user
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from models.product import Product
from models.wishlist import Wishlist
from exceptions import database_exception

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)

@router.post(
    "/",
    response_model=schemas.WishlistResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_wishlist(
    wishlist: schemas.WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        product = db.query(Product).filter(
            Product.id == wishlist.product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        if product.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add your own product to wishlist"
            )

        existing = db.query(Wishlist).filter(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == wishlist.product_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product already in wishlist"
            )

        new_wishlist = Wishlist(
            user_id=current_user.id,
            product_id=wishlist.product_id
        )

        db.add(new_wishlist)
        db.commit()
        db.refresh(new_wishlist)

        return new_wishlist

    except SQLAlchemyError:
        db.rollback()
        database_exception()
@router.get(
    "/",
    response_model=list[schemas.WishlistResponse]
)
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        wishlist = db.query(Wishlist).filter(
            Wishlist.user_id == current_user.id
        ).all()

        return wishlist

    except SQLAlchemyError:
        database_exception()
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_200_OK
)
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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