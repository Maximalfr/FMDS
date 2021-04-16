import os
from http import HTTPStatus
from logging import getLogger
from typing import List

import magic
from app import dependencies
from app.repositories import content as repository
from app import models
from app.schemas.content import ContentCreate, ContentRead, ContentPatch
from app.services.file import FileService
from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form,
                     HTTPException, Query, UploadFile)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.utils.keywords import normalize_keywords, split_keywords_generator

LOGGER = getLogger("fastapi")
VALID_MIMES_TYPES = ["image/gif", "image/jpeg", "image/png"]

router = APIRouter()


@router.get(
    "/contents/{filename}",
    tags=["contents"],
    description="Get a content entity as binary",
    status_code=HTTPStatus.OK,
    response_class=FileResponse,
)
async def get_content(
    filename: str,
    background_tasks: BackgroundTasks,
    count: bool = True,
    db: Session = Depends(dependency=dependencies.get_db),
):

    content = _get_content_or_not_found(filename, db)
    if not os.path.exists(content.filepath):
        # Should not append
        LOGGER.error(
            f"get_content. The file %s is not found but the entity exists",
            content.filepath,
        )
        _raise_content_not_found(filename)

    # increase asynchronously the counter
    if count:
        background_tasks.add_task(repository.increment_content_access, db, content.id)

    return FileResponse(content.filepath)


@router.post(
    "/contents",
    tags=["contents"],
    description="Create a content entity",
    status_code=HTTPStatus.CREATED,
    response_model=ContentRead,
)
async def upload_content(
    file: UploadFile = File(...),
    keywords: str = Form(...),
    file_service: FileService = Depends(dependency=dependencies.get_file_service),
    db: Session = Depends(dependency=dependencies.get_db),
):
    # File verification
    # Mime type
    mime_type = magic.from_buffer(await file.read(2048), mime=True)
    await file.seek(0)
    if mime_type not in VALID_MIMES_TYPES:
        raise HTTPException(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            detail=f"The media type '{mime_type}' is not supported",
        )

    # Keyword verification
    if len(keywords) == 0:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Empty keywords")

    keywords = list(normalize_keywords(split_keywords_generator(keywords)))
    filepath, filename = file_service.push(file, mimetype=mime_type)

    content_create = ContentCreate(
        filename=filename, filepath=filepath, keywords=keywords
    )

    # Create the response
    content = repository.create_content(db, content_create)
    return content


@router.get(
    "/contents/",
    tags=["contents"],
    description="Get contents by matching keywords",
    status_code=HTTPStatus.OK,
    response_model=List[ContentRead],
)
async def search_content_by_keywords(
    keywords: List[str] = Query(...),
    db: Session = Depends(dependency=dependencies.get_db),
):
    db_keywords = repository.get_contents_by_keywords(db, normalize_keywords(keywords))
    return db_keywords


@router.delete(
    "/contents/{filename}",
    tags=["contents"],
    description="Remove a content entity",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_content_by_id(
    filename: str,
    file_service: FileService = Depends(dependency=dependencies.get_file_service),
    db: Session = Depends(dependency=dependencies.get_db),
):
    content = _get_content_or_not_found(filename, db)

    # It is preferable that the entity is first deleted from the database.
    db.delete(content)
    db.commit()

    try:
        file_service.delete(content.filepath)
    except OSError or FileNotFoundError as e:
        LOGGER.error(
            f"delete_content_by_id. The file %s couldn't de deleted. %s",
            content.filepath,
            e,
        )


@router.patch(
    "/contents/{filename}",
    tags=["contents"],
    description="Update a content entity. For now, just the keywords",
    status_code=HTTPStatus.OK,
    response_model=ContentRead
)
async def update_content_by_id(
    filename: str,
    content_patch: ContentPatch,
    db: Session = Depends(dependency=dependencies.get_db),
):
    if len(content_patch.keywords) == 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="an entity must have at least one keyword"
        )
    keywords = normalize_keywords(content_patch.keywords)
    content = repository.update_content_keywords(db, filename, keywords)
    if content is None:
        _raise_content_not_found(filename)
    return content


def _get_content_or_not_found(filename: str, db: Session) -> models.Content:
    """
    Retrieve a content by its filename or raise a http not found exception
    :param filename: the content filename
    :return: the content model
    """
    content = repository.get_content_by_filename(db, filename)

    if content is None:
        _raise_content_not_found(filename)
    return content


def _raise_content_not_found(filename: str) -> None:
    """
    Raise a HTTPException with a not found status and a message
    :param filename: the filename of the not found content
    """
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail=f"content {filename} not found"
    )