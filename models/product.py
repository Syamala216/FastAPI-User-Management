from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    description = Column(String)

    price = Column(Float, nullable=False)

    stock = Column(Integer, nullable=False)

    category = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")

    wishlist = relationship(
        "Wishlist",
        back_populates="product"
    )