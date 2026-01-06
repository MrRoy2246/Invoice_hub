# app/main.py

from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import user, role, organization, association
from app.api.auth import router as auth_router
from app.utils.startup import init_system  # Import startup function
from app.api.shop import router as shop_router
from app.api.user_admin import router as user_admin_router
from app.api.product import router as product_router

app = FastAPI(title="InvoiceHub - Role Based System")

# Create tables
Base.metadata.create_all(bind=engine)
print("📦 Database tables created (if not exist)")

# Include auth router
app.include_router(auth_router, prefix="/auth")
print("🔑 Auth router included at /auth")
app.include_router(shop_router)
app.include_router(user_admin_router)
app.include_router(product_router)

# Run initialization at startup
@app.on_event("startup")
def startup_event():
    init_system()

@app.get("/")
def read_root():
    return {"message": "InvoiceHub Role-Based System Running"}
