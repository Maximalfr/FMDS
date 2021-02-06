from sqlalchemy.orm import Session

from app import models, schemas


def get_content_by_filename(db: Session, filename: str) -> models.Content:
    return db.query(models.Content).filter(models.Content.filename == filename).first()


def create_content(db: Session, content: schemas.ContentCreate):
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


def increment_content_access(db: Session, content_id: int):
    db.query(models.Content).filter_by(id=content_id).update(
        {models.Content.count: models.Content.count + 1}
    )
    db.commit()
