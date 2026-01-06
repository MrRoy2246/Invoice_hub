from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ShopCreate(BaseModel):
    name: str = Field(..., example="My Shop")
    address: Optional[str] = Field(None, example="123 Street")
    phone: Optional[str] = Field(None, example="0123456789")
    email: Optional[EmailStr] = Field(None, example="shop@example.com")

class ShopResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]

    class Config:
        orm_mode = True
