from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "changeme-use-a-real-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = "sqlite:///./cipherchat.db"

settings = Settings()
