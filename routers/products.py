from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models.product import Product
from models.user import User
from oauth2 import get_current_user
import schemas
from exceptions import database_exception



db_dependency = Depends(get_db)
user_dependency = Depends(get_current_user)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# CREATE PRODUCT
@router.post(
    "/",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:
        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock,
            category=product.category,
            owner_id=current_user.id
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product

    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        database_exception()


# GET ALL PRODUCTS
@router.get(
    "/",
    response_model=List[schemas.ProductResponse]
)
def get_products(
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:
        products = db.query(Product).all()

        return products

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# GET PRODUCT BY ID
@router.get(
    "/{product_id}",
    response_model=schemas.ProductResponse
)
def get_product(
    product_id: int,
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        return product

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# UPDATE PRODUCT
@router.put(
    "/{product_id}",
    response_model=schemas.ProductResponse
)
def update_product(
    product_id: int,
    updated_product: schemas.ProductCreate,
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Only owner can update
        if product.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this product"
            )

        product.name = updated_product.name
        product.description = updated_product.description
        product.price = updated_product.price
        product.stock = updated_product.stock
        product.category = updated_product.category

        db.commit()
        db.refresh(product)

        return product

    except SQLAlchemyError:
        db.rollback()
        database_exception()


# DELETE PRODUCT
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_product(
    product_id: int,
    db: Session = db_dependency,
    current_user: User = user_dependency
):
    try:
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Only owner can delete
        if product.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this product"
            )

        db.delete(product)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        database_exception()