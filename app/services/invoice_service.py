from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import extract
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product


# ==========================================================
# INVOICE NUMBER GENERATION
# ==========================================================
def generate_invoice_number(db: Session, shop_id: int) -> str:
    """
    Generate a sequential, year-based invoice number per shop.

    Format:
        INV-YYYY-000001

    Example:
        INV-2026-000042
    """
    current_year = datetime.utcnow().year

    last_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.shop_id == shop_id,
            extract("year", Invoice.created_at) == current_year
        )
        .order_by(Invoice.id.desc())
        .first()
    )

    if last_invoice:
        last_sequence = int(last_invoice.invoice_number.split("-")[-1])
        next_sequence = last_sequence + 1
    else:
        next_sequence = 1

    return f"INV-{current_year}-{next_sequence:06d}"


# ==========================================================
# INVOICE CREATION WORKFLOW
# ==========================================================
def create_invoice_service(
    db: Session,
    invoice_data,
    current_user
):
    """
    Core business logic for creating an invoice.

    Responsibilities:
    - Resolve shop context via RBAC
    - Generate invoice number
    - Validate products and stock
    - Calculate totals
    - Persist invoice and items
    - Update inventory
    """

    # ------------------------------------------------------
    # 1. Resolve shop context (RBAC)
    # ------------------------------------------------------
    role_names = [role.name for role in current_user.roles]

    if "shop_admin" in role_names:
        shop_id = current_user.organization_id
    elif "super_admin" in role_names:
        shop_id = getattr(invoice_data, "shop_id", None)
        if not shop_id:
            raise HTTPException(
                status_code=400,
                detail="shop_id is required for super admin"
            )
    else:
        raise HTTPException(
            status_code=403,
            detail="User does not have permission to create invoices"
        )

    # ------------------------------------------------------
    # 2. Generate invoice number
    # ------------------------------------------------------
    invoice_number = generate_invoice_number(db, shop_id)

    # ------------------------------------------------------
    # 3. Validate products and calculate totals
    # ------------------------------------------------------
    total_amount = 0
    prepared_items = []

    for item in invoice_data.items:
        product = (
            db.query(Product)
            .filter(
                Product.id == item.product_id,
                Product.shop_id == shop_id
            )
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found in shop"
            )

        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        line_total = product.price * item.quantity
        total_amount += line_total

        prepared_items.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.price,
            "total_price": line_total
        })

    # ------------------------------------------------------
    # 4. Persist invoice and items (transaction-safe)
    # ------------------------------------------------------
    try:
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_name=invoice_data.customer_name,
            customer_email=invoice_data.customer_email,
            total_amount=total_amount,
            shop_id=shop_id,
            created_by_id=current_user.id,
            payment_method=invoice_data.payment_method,  # new
            payment_status="pending"                     # new
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        for item in prepared_items:
            db.add(
                InvoiceItem(
                    invoice_id=invoice.id,
                    product_id=item["product"].id,
                    quantity=item["quantity"],
                    price=item["price"],
                    total_price=item["total_price"]
                )
            )

            # Reduce stock
            item["product"].quantity -= item["quantity"]
            db.add(item["product"])

        db.commit()
        db.refresh(invoice)

        return invoice

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create invoice"
        )
