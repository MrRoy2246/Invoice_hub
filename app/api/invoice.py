from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.invoice_schema import InvoiceCreate, InvoiceResponse
from app.api.dependencies import require_roles
from app.services.invoice_service import create_invoice_service
from app.models.invoice import Invoice

router = APIRouter(
    tags=["Invoices"],
    prefix="/invoices"
)

@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    db_invoice = create_invoice_service(
        db=db,
        invoice_data=invoice,
        current_user=current_user
    )

    print(
        f"🧾 Invoice {db_invoice.invoice_number} "
        f"created by {current_user.username}"
    )

    return db_invoice


@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    role_names = [role.name for role in current_user.roles]

    if "shop_admin" in role_names:
        invoices = (
            db.query(Invoice)
            .filter(Invoice.shop_id == current_user.organization_id)
            .all()
        )
    else:
        invoices = db.query(Invoice).all()

    print(
        f"📄 {current_user.username} fetched {len(invoices)} invoices"
    )

    return invoices
