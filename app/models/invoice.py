from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)

    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)

    sub_total = Column(Float, default=0)
    tax_rate = Column(Float, default=0)        # %
    tax_amount = Column(Float, default=0)
    discount_type = Column(String, nullable=True)  
    # values: "flat" or "percentage"
    discount_value = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0)

    payment_method = Column(String, nullable=True)
    payment_status = Column(String, default="pending")

    shop_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    shop = relationship("Organization", back_populates="invoices")
    created_by = relationship("User")
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")
