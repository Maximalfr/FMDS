from fastapi import FastAPI

from app.database import Base, engine
from app.routers import contents

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(contents.router, prefix="/api/v1")
