from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.database import get_db
from app.models.user import User
from app.models.role import Role
from app.models.organization import Organization
from app.schemas.user_schema import ShopAdminCreate
from app.api.dependencies import require_roles

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(tags=["Users"], prefix="/users")

@router.post("/shop-admin")
def create_shop_admin(admin: ShopAdminCreate, db: Session = Depends(get_db), current_user=Depends(require_roles(["super_admin"]))):
    # Check shop exists
    shop = db.query(Organization).filter(Organization.id == admin.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    # Check email uniqueness
    existing_user = db.query(User).filter(User.email == admin.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(admin.password)
    shop_admin_role = db.query(Role).filter(Role.name == "shop_admin").first()
    if not shop_admin_role:
        raise HTTPException(status_code=500, detail="Shop Admin role missing")

    user = User(
        username=admin.username,
        email=admin.email,
        hashed_password=hashed_password,
        organization_id=shop.id
    )
    user.roles.append(shop_admin_role)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"🔑 Shop Admin '{user.username}' created for shop '{shop.name}' by Super Admin '{current_user.username}'")
    return {"message": f"Shop Admin '{user.username}' created successfully"}
