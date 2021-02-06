from functools import lru_cache

from app import config
from app.database import SessionLocal
from app.services.file import FileService


@lru_cache
def get_settings():
    return config.Settings()


@lru_cache
def get_file_service():
    return FileService(get_settings())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
