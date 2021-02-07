import os
from http import HTTPStatus
from logging import getLogger
from typing import List

import magic
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import dependencies
from app.repositories import content as repository
from app.schemas.content import ContentCreate, ContentRead
from app.services.file import FileService

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
    not_found_error = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="content not found"
    )

    content = repository.get_content_by_filename(db, filename)

    if content is None:
        raise not_found_error
    elif not os.path.exists(content.filepath):
        # Should not append
        LOGGER.error(
            f"get_content. The file %s is not found but the entity exists",
            content.filepath,
        )
        raise not_found_error

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

    keywords = keywords.replace(" ", "").split(",")
    filepath, filename = file_service.push(file, mimetype=mime_type)

    content_create = ContentCreate(
        filename=filename, filepath=filepath, keywords=keywords
    )

    # Create the response
    content = repository.create_content(db, content_create)
    content_read = ContentRead(
        filename=content.filename,
        # Keyword schema to strings list
        keywords=[k.name for k in content.keywords],
    )
    return content_read


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
    db_keywords = repository.get_contents_by_keywords(db, keywords)
    return db_keywords
