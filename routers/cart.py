from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from logging_config import info_logger

import schemas
from database import get_db
from models.user import User
from models.product import Product
from models.cart import Cart
from oauth2 import get_current_user
from exceptions import database_exception


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


# ADD TO CART
@router.post(
    "/",
    response_model=schemas.CartResponse,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
    cart: schemas.CartCreate,
    db: DbSession,
    current_user: CurrentUser
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

        if product.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot add your own product to cart"
            )

        if cart.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )

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

            if existing.quantity + cart.quantity > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Requested quantity exceeds available stock"
                )

            existing.quantity += cart.quantity

            db.commit()
            db.refresh(existing)


            info_logger.info(
                f"User ID: {current_user.id} - "
                f"Updated cart quantity - "
                f"Product ID: {product.id} - "
                f"Quantity: {existing.quantity}"
            )

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

        # Log new cart item
        info_logger.info(
            f"User ID: {current_user.id} - "
            f"Added product to cart - "
            f"Product ID: {product.id} - "
            f"Quantity: {new_cart.quantity}"
        )

        return {
            "id": new_cart.id,
            "user_id": new_cart.user_id,
            "product_name": product.name,
            "quantity": new_cart.quantity
        }

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# GET CART
@router.get(
    "/",
    response_model=list[schemas.CartResponse]
)
def get_cart(
    db: DbSession,
    current_user: CurrentUser
):
    try:

        cart_items = db.query(Cart).filter(
            Cart.user_id == current_user.id
        ).all()

        result = []

        for item in cart_items:

            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            if product is None:
                continue

            result.append({
                "id": item.id,
                "user_id": item.user_id,
                "product_name": product.name,
                "quantity": item.quantity
            })

        return result

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# DELETE CART ITEM
@router.delete(
    "/{cart_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_from_cart(
    cart_id: int,
    db: DbSession,
    current_user: CurrentUser
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

        product_id = cart_item.product_id

        db.delete(cart_item)
        db.commit()

        # Log cart item removal
        info_logger.info(
            f"User ID: {current_user.id} - "
            f"Removed product from cart - "
            f"Product ID: {product_id} - "
            f"Cart ID: {cart_id}"
        )

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)