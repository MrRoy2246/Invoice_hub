from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_super_admin(db: Session, username: str, email: str, password: str):
    """
    Creates a Super Admin user with given credentials
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        print("Super Admin already exists")
        return user

    # hashed_password = pwd_context.hash(password)
    hashed_password = pwd_context.hash(password[:72])
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    if not super_admin_role:
        raise Exception("Super Admin role does not exist. Run init_roles first.")

    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        organization_id=None  # Super Admin is global
    )
    user.roles.append(super_admin_role)
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Super Admin created.")
    return user
