from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.dependencies import require_roles
from app.services.report_service import get_sales_summary

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/sales-summary")
def sales_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    if "shop_admin" in [r.name for r in current_user.roles]:
        shop_id = current_user.organization_id
    else:
        return {"message": "Super admin global report coming soon"}

    summary = get_sales_summary(db, shop_id)
    print(f"📊 Sales summary fetched for shop {shop_id}")
    return summary
