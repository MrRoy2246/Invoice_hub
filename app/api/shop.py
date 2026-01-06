from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.organization import Organization
from app.schemas.shop_schema import ShopCreate, ShopResponse
from app.api.dependencies import require_roles

router = APIRouter(tags=["Shops"], prefix="/shops")

@router.post("/", response_model=ShopResponse)
def create_shop(shop: ShopCreate, db: Session = Depends(get_db), current_user=Depends(require_roles(["super_admin"]))):
    db_shop = Organization(**shop.dict())
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)
    print(f"🛒 Shop '{db_shop.name}' created by Super Admin '{current_user.username}'")
    return db_shop

@router.get("/", response_model=list[ShopResponse])
def list_shops(db: Session = Depends(get_db), current_user=Depends(require_roles(["super_admin"]))):
    shops = db.query(Organization).all()
    print(f"📦 Super Admin '{current_user.username}' fetched {len(shops)} shops")
    return shops
