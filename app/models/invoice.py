from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    total_amount = Column(Float, default=0)
    shop_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # ✅ Payment fields
    payment_method = Column(String, nullable=True)        # Cash, Card, Mobile banking, etc.
    payment_status = Column(String, default="pending")   # pending, paid, failed

    shop = relationship("Organization", back_populates="invoices")
    created_by = relationship("User")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint(
            "shop_id",
            "invoice_number",
            name="uq_invoice_number_per_shop"
        ),
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
