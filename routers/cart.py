from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import schemas
from database import get_db
from models.user import User
from models.product import Product
from models.cart import Cart
from oauth2 import get_current_user
from exceptions import database_exception


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.post(
    "/",
    response_model=schemas.CartResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
    cart: schemas.CartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        product = db.query(Product).filter(
            Product.id == cart.product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # User cannot add their own product
        if product.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add your own product to cart"
            )

        # Quantity validation
        if cart.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )

        # Check requested quantity
        if cart.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity is not available"
            )

        existing = db.query(Cart).filter(
            Cart.user_id == current_user.id,
            Cart.product_id == cart.product_id
        ).first()

        if existing:

            # Check total quantity
            if existing.quantity + cart.quantity > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Requested quantity exceeds available stock"
                )

            existing.quantity += cart.quantity

            db.commit()
            db.refresh(existing)

            return {
                "id": existing.id,
                "user_id": existing.user_id,
                "product_name": product.name,
                "quantity": existing.quantity
            }

        new_cart = Cart(
            user_id=current_user.id,
            product_id=cart.product_id,
            quantity=cart.quantity
        )

        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)

        return {
            "id": new_cart.id,
            "user_id": new_cart.user_id,
            "product_name": product.name,
            "quantity": new_cart.quantity
        }

    except SQLAlchemyError:
        db.rollback()
        database_exception()


@router.get(
    "/",
    response_model=list[schemas.CartResponse]
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        cart_items = db.query(Cart).filter(
            Cart.user_id == current_user.id
        ).all()

        result = []

        for item in cart_items:
            result.append({
                "id": item.id,
                "user_id": item.user_id,
                "product_name": item.product.name,
                "quantity": item.quantity
            })

        return result

    except SQLAlchemyError:
        db.rollback()
        database_exception()


@router.delete(
    "/{cart_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_from_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        cart_item = db.query(Cart).filter(
            Cart.id == cart_id,
            Cart.user_id == current_user.id
        ).first()

        if cart_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        db.delete(cart_item)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        database_exception()