from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InvoiceItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class InvoiceCreate(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    items: List[InvoiceItemCreate]
    payment_method: Optional[str] = None  # ✅ New

class InvoiceItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float
    total_price: float

    class Config:
        orm_mode = True

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    customer_name: str
    customer_email: Optional[str]
    total_amount: float
    shop_id: int
    created_by_id: int
    created_at: datetime
    payment_method: Optional[str]  # ✅ New
    payment_status: str            # ✅ New
    items: List[InvoiceItemResponse]

    class Config:
        orm_mode = True
