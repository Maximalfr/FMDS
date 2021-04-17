from app.config import Settings
from app.models.user import User

from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"


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
            "exp": datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)
        }
        return jwt.encode(to_encode, self.settings.secret_key, algorithm=ALGORITHM)
