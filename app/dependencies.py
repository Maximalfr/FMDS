from functools import lru_cache

from app import config, services
from app.database import SessionLocal


@lru_cache
def get_settings():
    return config.Settings()


@lru_cache
def get_file_service() -> services.FileService:
    return services.FileService(get_settings())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache
def get_security_service() -> services.SecurityService:
    return services.SecurityService(get_settings())


@lru_cache
def get_jwt_bearer_service() -> services.JWTBearerService:
    return services.JWTBearerService(next(get_db()), get_security_service())
