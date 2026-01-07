from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import extract
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product


# 🔢 Invoice Number Generator
def generate_invoice_number(db: Session, shop_id: int) -> str:
    year = datetime.utcnow().year

    last_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.shop_id == shop_id,
            extract("year", Invoice.created_at) == year
        )
        .order_by(Invoice.id.desc())
        .first()
    )

    next_seq = (
        int(last_invoice.invoice_number.split("-")[-1]) + 1
        if last_invoice else 1
    )

    return f"INV-{year}-{next_seq:06d}"


# 💸 Discount Calculation
def calculate_discount(
    sub_total: float,
    discount_type: str | None,
    discount_value: float
) -> float:
    if not discount_type or discount_value <= 0:
        return 0.0

    if discount_type == "flat":
        return min(discount_value, sub_total)

    if discount_type == "percentage":
        return sub_total * (discount_value / 100)

    return 0.0


# 🧠 Create Invoice Logic
def create_invoice_service(db: Session, invoice_data, current_user):
    role_names = [role.name for role in current_user.roles]

    # 🏪 Determine shop
    if "shop_admin" in role_names:
        shop_id = current_user.organization_id
    else:
        shop_id = invoice_data.shop_id
        if not shop_id:
            raise HTTPException(
                status_code=400,
                detail="shop_id is required for super admin"
            )

    invoice_number = generate_invoice_number(db, shop_id)

    invoice_items_data = []
    sub_total = 0.0

    # 📦 Validate products & stock
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
                detail=f"Product {item.product_id} not found"
            )

        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        total_price = product.price * item.quantity
        sub_total += total_price

        invoice_items_data.append(
            (product, item.quantity, product.price, total_price)
        )

    # 🧮 Discount
    discount_amount = calculate_discount(
        sub_total=sub_total,
        discount_type=invoice_data.discount_type,
        discount_value=invoice_data.discount_value or 0
    )

    # 🧾 Tax
    tax_rate = invoice_data.tax_rate or 0
    taxable_amount = sub_total - discount_amount
    tax_amount = (taxable_amount * tax_rate) / 100

    # 💰 Grand Total
    grand_total = taxable_amount + tax_amount

    try:
        # 🧾 Create Invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_name=invoice_data.customer_name,
            customer_email=invoice_data.customer_email,

            sub_total=sub_total,

            discount_type=invoice_data.discount_type,
            discount_value=invoice_data.discount_value or 0,
            discount_amount=discount_amount,

            tax_rate=tax_rate,
            tax_amount=tax_amount,

            grand_total=grand_total,

            payment_method=invoice_data.payment_method,
            payment_status=invoice_data.payment_status,

            shop_id=shop_id,
            created_by_id=current_user.id
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        # 📦 Create Invoice Items & reduce stock
        for product, quantity, price, total_price in invoice_items_data:
            db.add(
                InvoiceItem(
                    invoice_id=invoice.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=price,
                    total_price=total_price
                )
            )

            product.quantity -= quantity
            db.add(product)

        db.commit()
        db.refresh(invoice)

        return invoice

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create invoice"
        )
