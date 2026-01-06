from pydantic_settings  import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Super Admin credentials
    SUPERADMIN_USERNAME: str
    SUPERADMIN_EMAIL: str
    SUPERADMIN_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()
