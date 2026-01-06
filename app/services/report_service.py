from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.invoice import Invoice

def get_sales_summary(db: Session, shop_id: int):
    total_sales = db.query(func.sum(Invoice.total_amount)) \
        .filter(Invoice.shop_id == shop_id).scalar() or 0

    total_invoices = db.query(func.count(Invoice.id)) \
        .filter(Invoice.shop_id == shop_id).scalar()

    return {
        "total_sales": float(total_sales),
        "total_invoices": total_invoices
    }
