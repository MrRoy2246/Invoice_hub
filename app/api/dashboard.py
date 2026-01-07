from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.db.database import get_db
from app.api.dependencies import require_roles
from app.services.dashboard_service import get_dashboard_summary,get_daily_revenue_chart,get_monthly_revenue_chart,get_invoice_list


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    role_names = [role.name for role in current_user.roles]

    if "shop_admin" in role_names:
        shop_id = current_user.organization_id
    else:
        shop_id = None

    return get_dashboard_summary(db, shop_id)



@router.get("/charts/daily")
def daily_chart(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    shop_id = current_user.organization_id if "shop_admin" in [r.name for r in current_user.roles] else None
    return get_daily_revenue_chart(db, shop_id, days)


@router.get("/charts/monthly")
def monthly_chart(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    shop_id = current_user.organization_id if "shop_admin" in [r.name for r in current_user.roles] else None
    return get_monthly_revenue_chart(db, shop_id, months)

@router.get("/invoices")
def invoice_dashboard_list(
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    shop_id = current_user.organization_id if "shop_admin" in [r.name for r in current_user.roles] else None
    return get_invoice_list(db, shop_id, status, date_from, date_to, page, limit)