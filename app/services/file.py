import mimetypes
import os
import shutil
from typing import Tuple

import timeflake
from fastapi import UploadFile

from app.config import Settings


class FileService:
    """Service that handle all saving aspect of content files"""

    def __init__(self, settings: Settings):
        """
        Construct the file service
        :param settings: the settings object needed to get the upload_directory path
        """
        self._upload_directory = settings.upload_directory

        # Check if the directory exists or create it
        if not os.path.isdir(self._upload_directory):
            os.makedirs(self._upload_directory)

    def push(self, file: UploadFile, mimetype: str = None) -> Tuple[str, str]:
        """
        Save an uploaded file into the file directory.
        It will generate a random name and will handle all the saving things.
        :param file: the file to save
        :param mimetype: use the specified mimetype instead of the file.content_type mime type
        :return: a tuple with the complete filepath (where the file is saved)
        and the file name
        """
        # Create new file name
        mimetype = mimetype or file.content_type
        ext = mimetypes.guess_extension(mimetype)
        name = timeflake.random().base62
        filename = name + ext

        # Generate filepath
        # The first dir is a part of the timestamp
        # The second is the last letter of the random part
        dirs = os.path.join(self._upload_directory, filename[:5], name[-1])
        os.makedirs(dirs, exist_ok=True)
        filepath = os.path.join(dirs, filename)

        with open(filepath, mode="wb") as fp:
            shutil.copyfileobj(file.file, fp)

        return filepath, filename
