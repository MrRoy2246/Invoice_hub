from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product
from app.schemas.invoice_schema import InvoiceCreate, InvoiceResponse
from app.api.dependencies import require_roles
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(tags=["Invoices"], prefix="/invoices")

@router.post("/", response_model=InvoiceResponse)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db),
                   current_user=Depends(require_roles(["shop_admin", "super_admin"]))):
    # Determine shop
    shop_id = current_user.organization_id if "shop_admin" in [role.name for role in current_user.roles] else None
    if shop_id is None and "super_admin" in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=400, detail="Super Admin must specify shop_id")

    # Calculate total and check product availability
    total_amount = 0
    invoice_items = []

    for item in invoice.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.shop_id == shop_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found in shop")
        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

        total_price = product.price * item.quantity
        total_amount += total_price
        invoice_items.append((product, item.quantity, product.price, total_price))

    # Create Invoice
    db_invoice = Invoice(
        customer_name=invoice.customer_name,
        customer_email=invoice.customer_email,
        total_amount=total_amount,
        shop_id=shop_id,
        created_by_id=current_user.id
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    # Create Invoice Items and update product quantity
    for product, quantity, price, total_price in invoice_items:
        invoice_item = InvoiceItem(
            invoice_id=db_invoice.id,
            product_id=product.id,
            quantity=quantity,
            price=price,
            total_price=total_price
        )
        product.quantity -= quantity
        db.add(invoice_item)
        db.add(product)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create invoice")

    db.refresh(db_invoice)
    print(f"💰 Invoice {db_invoice.id} created by '{current_user.username}' for shop_id {shop_id}")
    return db_invoice

# List invoices
@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(db: Session = Depends(get_db),
                  current_user=Depends(require_roles(["shop_admin", "super_admin"]))):
    if "shop_admin" in [role.name for role in current_user.roles]:
        invoices = db.query(Invoice).filter(Invoice.shop_id == current_user.organization_id).all()
    else:
        invoices = db.query(Invoice).all()

    print(f"📄 '{current_user.username}' fetched {len(invoices)} invoices")
    return invoices
