from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ShopAdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    shop_id: int = Field(..., example=1)
