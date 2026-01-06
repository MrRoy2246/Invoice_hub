# app/utils/startup.py

from app.db.database import SessionLocal
from app.utils.init_roles import create_initial_roles
from app.utils.init_super_admin import create_super_admin
from app.core.config import settings  
def init_system():
    """
    Initialize the system at app startup:
    - Create initial roles if not exist
    - Create Super Admin user if not exist
    """
    print("🚀 Starting system initialization...")

    db = SessionLocal()
    try:
        # Create roles
        create_initial_roles(db)
        print("✅ Initial roles checked/created")

        # Create Super Admin
        create_super_admin(
            db,
            username=settings.SUPERADMIN_USERNAME,
            email=settings.SUPERADMIN_EMAIL,
            password=settings.SUPERADMIN_PASSWORD
        )
        print("✅ Super Admin checked/created")

    except Exception as e:
        print(f"❌ Error during system initialization: {e}")
    finally:
        db.close()
        print("🔒 Database session closed")
        print("🎉 System initialization complete!")
