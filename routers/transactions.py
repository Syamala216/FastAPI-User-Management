from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from logging_config import info_logger

import schemas
from database import get_db
from models.user import User
from models.product import Product
from models.transaction import Transaction
from oauth2 import get_current_user
from exceptions import database_exception


DbSession = Annotated[
    Session,
    Depends(get_db)
]

CurrentUser = Annotated[
    User,
    Depends(get_current_user)
]


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# CREATE TRANSACTION
@router.post(
    "/",
    response_model=schemas.TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: DbSession,
    current_user: CurrentUser
):
    try:
        # Check product
        product = db.query(Product).filter(
            Product.id == transaction.product_id
        ).first()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # User cannot purchase own product
        if product.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot purchase your own product"
            )

        # Quantity validation
        if transaction.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )

        # Stock validation
        if transaction.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity is not available"
            )

        # Payment validation
        if transaction.payment_status not in ["success", "failure"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment status must be success or failure"
            )

        # Calculate total
        total_amount = product.price * transaction.quantity

        # Create transaction
        new_transaction = Transaction(
            user_id=current_user.id,
            product_id=transaction.product_id,
            quantity=transaction.quantity,
            total_amount=total_amount,
            payment_status=transaction.payment_status
        )

        db.add(new_transaction)

        # Reduce stock only after successful payment
        if transaction.payment_status == "success":
            product.stock -= transaction.quantity

        db.commit()
        db.refresh(new_transaction)

        # Log successful transaction
        info_logger.info(
            f"User ID: {current_user.id} - "
            f"Created transaction - "
            f"Transaction ID: {new_transaction.id} - "
            f"Product ID: {product.id} - "
            f"Quantity: {transaction.quantity} - "
            f"Payment: {transaction.payment_status} - "
            f"Total: {total_amount}"
        )

        return new_transaction

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)


# GET TRANSACTIONS
@router.get(
    "/",
    response_model=list[schemas.TransactionResponse]
)
def get_transactions(
    db: DbSession,
    current_user: CurrentUser
):
    try:
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id
        ).all()

        return transactions

    except SQLAlchemyError as e:
        db.rollback()
        database_exception(e)