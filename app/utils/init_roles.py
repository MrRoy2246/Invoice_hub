from sqlalchemy.orm import Session
from app.models.role import Role

def create_initial_roles(db: Session):
    """
    Create initial roles if they do not exist.
    Roles: Super Admin, Shop Admin
    """
    roles = [
        {"name": "super_admin", "description": "Full system access"},
        {"name": "shop_admin", "description": "Access only for their shop"}
    ]

    for role_data in roles:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(**role_data)
            db.add(role)
    db.commit()
    print("Initial roles created (if not existed).")
