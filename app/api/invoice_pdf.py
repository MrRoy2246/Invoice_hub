from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.invoice import Invoice
from app.api.dependencies import require_roles
from app.services.pdf_service import generate_invoice_pdf

router = APIRouter(prefix="/invoices", tags=["Invoice PDF"])

@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["shop_admin", "super_admin"]))
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Shop RBAC
    if "shop_admin" in [r.name for r in current_user.roles]:
        if invoice.shop_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")

    pdf_buffer = generate_invoice_pdf(invoice)

    print(f"📄 Invoice PDF generated for invoice {invoice.invoice_number}")

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"}
    )
