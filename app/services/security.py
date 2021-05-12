from datetime import datetime, timedelta

from fastapi import Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from app.config import Settings
from app.models.user import User
from app.repositories.user import get_user
from app.schemas.security import TokenData

ALGORITHM = jwt.ALGORITHMS.HS512


class SecurityService:
    """Service that handle all security aspect for a user"""

    def __init__(self, settings: Settings):
        """
        Construct the security service
        :param settings: the settings object needed to get some security settings
        """
        self.pdw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.settings = settings

    def authenticate_user(self, user: User, password: str) -> bool:
        """
        Tell if the password is the same that the user password
        :param user: the user to test
        :param password: the plain text password
        :return: True if the password is correct or False otherwise
        """
        return self.pdw_context.verify(password, user.hashed_password)

    def create_access_token(self, user: User):
        """
        Create a JWT for an user.
        :param user: the specified user
        :return: the new JWT
        """
        to_encode = {
            "username": user.username,
            "exp": datetime.utcnow()
            + timedelta(minutes=self.settings.access_token_expire_minutes),
        }
        return jwt.encode(to_encode, self.settings.secret_key, algorithm=ALGORITHM)

    def check_user_token(self, token: str) -> TokenData:
        """
        Check an user's token and return its information.
        If the token is invalid or expired, raise a JWTError
        :param token: the token to parse
        :return: the token data
        :raise JWTError: the token is invalid
        """
        payload = jwt.decode(token, self.settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        return TokenData(username=username)


# Not fan to raise HTTP error from service..
class JWTBearerService:
    """Service that handle JWT validation for routes"""

    def __init__(self, db: Session, security_service: SecurityService):
        """
        Construct the security service
        :param db: the database session
        :param security_service: the security service to check the tokens
        """
        self.db = db
        self.security_service = security_service

    async def __call__(self, authorization: str = Header("")) -> User:
        """
        Check the token for an user if valid, return the User model.
        Otherwise, raise an http exception (401)
        :param authorization: the authorization header that contains the bearer token
        :return: the User model
        """
        auth = authorization.split(" ")
        if len(auth) != 2 or auth[0].lower() != "bearer" or auth[1] == "":
            raise _get_jwt_http_exception()
        try:
            token_data = self.security_service.check_user_token(auth[1])
            user = get_user(self.db, token_data.username)
            print(user)
            if user is None:
                raise _get_jwt_http_exception()
        except JWTError as e:
            # todo log error
            raise _get_jwt_http_exception(format(e))
        return user


def _get_jwt_http_exception(message: str = "Could not validate credentials"):
    """
    Get the HTTP exception for JWT validation.
    :param message: The message to send
    :return: the crafted HTTP exception
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )
