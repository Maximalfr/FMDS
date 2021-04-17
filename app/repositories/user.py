from sqlalchemy.orm import Session

from app import models


def get_user(db: Session, username: str) -> models.User:
    """
    Retrieve an user by its username
    :param db: The session database object
    :param username: The user's username
    :return: The User model or None
    """
    return db.query(models.User).filter(models.User.username == username).first()
