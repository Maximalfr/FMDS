from typing import Iterator, List

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app import models, schemas


def get_content_by_filename(db: Session, filename: str) -> [models.Content, None]:
    """
    Retrieve a content entity by its filename
    :param db: The session database object
    :param filename: The content filename
    :return: The Content model or None
    """
    return db.query(models.Content).filter(models.Content.filename == filename).first()


def create_content(db: Session, content: schemas.ContentCreate) -> models.Content:
    """
    Create a content entity, the keywords if they don't exists and save it into the
    database.
    :param db: The session database object
    :param content: The content schema to create
    :return: The created content entity
    """

    # Retrieve existing keywords
    keywords = content.keywords
    db_keywords = (
        db.query(models.Keyword).filter(models.Keyword.name.in_(keywords)).all()
    )

    # Find missing keywords entities and create them
    for db_keyword in db_keywords:
        keywords.remove(db_keyword.name)
    for keyword in keywords:
        db_keywords.append(models.Keyword(name=keyword))

    # Create the content entity
    db_content = models.Content(
        filename=content.filename, filepath=content.filepath, keywords=db_keywords
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content


def increment_content_access(db: Session, content_id: int) -> None:
    """
    Increment the access counter for a content entity.
    :param db: The session database object
    :param content_id: The content entity id
    """
    db.query(models.Content).filter_by(id=content_id).update(
        {models.Content.count: models.Content.count + 1}
    )
    db.commit()


def get_contents_by_keywords(
    db: Session, keywords: [Iterator[str], List[str]]
) -> List[models.Content]:
    """
    Retrieves content that matches at least one keyword.
    The list is ordered by the number of matched keywords.
    :param db: The session database object
    :param keywords:
    :return: The ordered list of matched contents
    """
    return (
        db.query(models.Content)
        .join(models.Content, models.Keyword.contents)
        .filter(models.Keyword.name.in_(keywords))
        .group_by(models.Content.id)
        .order_by(desc(func.count()))
        .all()
    )


def update_content_keywords(
    db: Session, filename: str, keywords: [Iterator[str], List[str]]
) -> [models.Content, None]:
    """
    Update a content entity, create the keywords if they don't exists and save it into the
    database.
    :param db: The session database object
    :param filename: The content filename
    :param keywords: The new keywords for the entity
    :return: The updated content entity or None if it doesn't exist
    """

    content = get_content_by_filename(db, filename)
    if content is None:
        return None

    # Retrieve existing keywords
    db_keywords = (
        db.query(models.Keyword).filter(models.Keyword.name.in_(keywords)).all()
    )

    # Find missing keywords entities and create them
    for db_keyword in db_keywords:
        keywords.remove(db_keyword.name)
    for keyword in keywords:
        db_keywords.append(models.Keyword(name=keyword))

    # Update the content entity
    content.keywords = db_keywords
    db.add(content)
    db.commit()
    db.refresh(content)
    return content
