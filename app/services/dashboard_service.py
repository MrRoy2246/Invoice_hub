from datetime import timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.invoice import Invoice


def get_dashboard_summary(db: Session, shop_id: int | None = None):
    today = date.today()
    start_of_month = today.replace(day=1)

    base_query = db.query(Invoice)

    if shop_id:
        base_query = base_query.filter(Invoice.shop_id == shop_id)

    total_revenue = (
        base_query.with_entities(func.coalesce(func.sum(Invoice.grand_total), 0))
        .scalar()
    )

    today_revenue = (
        base_query
        .filter(func.date(Invoice.created_at) == today)
        .with_entities(func.coalesce(func.sum(Invoice.grand_total), 0))
        .scalar()
    )

    monthly_revenue = (
        base_query
        .filter(Invoice.created_at >= start_of_month)
        .with_entities(func.coalesce(func.sum(Invoice.grand_total), 0))
        .scalar()
    )

    total_invoices = base_query.count()

    paid_invoices = base_query.filter(
        Invoice.payment_status == "paid"
    ).count()

    pending_invoices = base_query.filter(
        Invoice.payment_status != "paid"
    ).count()

    total_discount = (
        base_query.with_entities(func.coalesce(func.sum(Invoice.discount_amount), 0))
        .scalar()
    )

    total_tax = (
        base_query.with_entities(func.coalesce(func.sum(Invoice.tax_amount), 0))
        .scalar()
    )

    return {
        "total_revenue": float(total_revenue),
        "today_revenue": float(today_revenue),
        "monthly_revenue": float(monthly_revenue),
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "pending_invoices": pending_invoices,
        "total_discount": float(total_discount),
        "total_tax": float(total_tax)
    }



def get_daily_revenue_chart(db, shop_id: int | None, days: int = 7):
    start_date = date.today() - timedelta(days=days - 1)

    query = (
        db.query(
            func.date(Invoice.created_at).label("date"),
            func.sum(Invoice.grand_total).label("total")
        )
        .filter(Invoice.created_at >= start_date)
        .group_by(func.date(Invoice.created_at))
        .order_by(func.date(Invoice.created_at))
    )

    if shop_id:
        query = query.filter(Invoice.shop_id == shop_id)

    data = query.all()

    return [
        {"date": str(row.date), "total": float(row.total)}
        for row in data
    ]


def get_monthly_revenue_chart(db, shop_id: int | None, months: int = 6):
    query = (
        db.query(
            func.date_trunc("month", Invoice.created_at).label("month"),
            func.sum(Invoice.grand_total).label("total")
        )
        .group_by(func.date_trunc("month", Invoice.created_at))
        .order_by(func.date_trunc("month", Invoice.created_at))
    )

    if shop_id:
        query = query.filter(Invoice.shop_id == shop_id)

    data = query.limit(months).all()

    return [
        {
            "month": row.month.strftime("%Y-%m"),
            "total": float(row.total)
        }
        for row in data
    ]


def get_invoice_list(
    db,
    shop_id: int | None,
    status: str | None,
    date_from: date | None,
    date_to: date | None,
    page: int,
    limit: int
):
    query = db.query(Invoice)

    if shop_id:
        query = query.filter(Invoice.shop_id == shop_id)

    if status:
        query = query.filter(Invoice.payment_status == status)

    if date_from:
        query = query.filter(Invoice.created_at >= date_from)

    if date_to:
        query = query.filter(Invoice.created_at <= date_to)

    total = query.count()

    invoices = (
        query.order_by(Invoice.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": invoices
    }
