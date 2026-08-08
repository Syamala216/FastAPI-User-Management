from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    product_id = Column(Integer, ForeignKey("product.id"))

    quantity = Column(Integer, nullable=False)

    total_amount = Column(Float, nullable=False)

    payment_status = Column(String(20), nullable=False)

    user = relationship("User")

    product = relationship("Product")