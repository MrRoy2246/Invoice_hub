from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.api.dependencies import require_roles, get_current_user

router = APIRouter(tags=["Products"], prefix="/products")

# Create Product
@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db),
                   current_user=Depends(require_roles(["shop_admin", "super_admin"]))):
    shop_id = current_user.organization_id if "shop_admin" in [role.name for role in current_user.roles] else None
    if shop_id is None and "super_admin" in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=400, detail="Super Admin must specify shop_id when creating product")
    
    db_product = Product(**product.dict(), shop_id=shop_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    print(f"🛠 Product '{db_product.name}' created by '{current_user.username}' for shop_id {db_product.shop_id}")
    return db_product

# List Products
@router.get("/", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db), current_user=Depends(require_roles(["shop_admin", "super_admin"]))):
    if "shop_admin" in [role.name for role in current_user.roles]:
        products = db.query(Product).filter(Product.shop_id == current_user.organization_id).all()
    else:
        products = db.query(Product).all()
    print(f"📦 '{current_user.username}' fetched {len(products)} products")
    return products

# Update Product
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db),
                   current_user=Depends(require_roles(["shop_admin", "super_admin"]))):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if "shop_admin" in [role.name for role in current_user.roles] and db_product.shop_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not allowed to modify products of another shop")
    
    for field, value in product.dict(exclude_unset=True).items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    print(f"🔧 Product '{db_product.name}' updated by '{current_user.username}'")
    return db_product

# Delete Product
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db),
                   current_user=Depends(require_roles(["shop_admin", "super_admin"]))):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if "shop_admin" in [role.name for role in current_user.roles] and db_product.shop_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not allowed to delete products of another shop")
    
    db.delete(db_product)
    db.commit()
    print(f"🗑 Product '{db_product.name}' deleted by '{current_user.username}'")
    return {"message": "Product deleted successfully"}
