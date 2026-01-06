from pydantic import BaseModel, Field
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = Field(..., ge=0)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    quantity: int
    shop_id: int
    is_active: bool

    class Config:
        orm_mode = True
