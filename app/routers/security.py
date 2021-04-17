from logging import getLogger

from app import dependencies, models, repositories, schemas
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.services import SecurityService

LOGGER = getLogger("fastapi")

router = APIRouter()


@router.post(
    "/token",
    tags=["security"],
    description="Authenticate an user and retrieve a JWT",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Token
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(dependency=dependencies.get_db),
        security_service: SecurityService = Depends(dependency=dependencies.get_security_service)
):
    user = repositories.user.get_user(db, form_data.username)
    if not user or not security_service.authenticate_user(user, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": security_service.create_access_token(user), "token_type": "bearer"}
