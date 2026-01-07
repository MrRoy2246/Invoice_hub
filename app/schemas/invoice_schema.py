from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InvoiceItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)

class InvoiceCreate(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    discount_type: Optional[str] = Field(
        None, description="flat or percentage"
    )
    discount_value: Optional[float] = Field(
        0.0, ge=0
    )
    tax_rate: Optional[float] = Field(default=0, ge=0, le=100)
    payment_method: Optional[str] = None  # ✅ New
    payment_status: Optional[str] = Field(default="paid")
    items: List[InvoiceItemCreate]
    

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

    sub_total: float
    discount_type: Optional[str]
    discount_value: float
    discount_amount: float
    tax_rate: float
    tax_amount: float
    grand_total: float

    payment_method: Optional[str]
    payment_status: Optional[str]

    shop_id: int
    created_by_id: int
    created_at: datetime

    items: List[InvoiceItemResponse]

    class Config:
        orm_mode = True
