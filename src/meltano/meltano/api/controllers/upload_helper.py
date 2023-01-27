from __future__ import annotations

from os import SEEK_END
from os.path import join

from meltano.core.project import Project

from .utils import enforce_secure_filename

MAX_FILE_SIZE = 4194304  # 4MB max
ALLOWED_EXTENSIONS = {"json"}


class InvalidFileTypeError(Exception):
    """Occurs when a file does not meet our file type criteria."""

    def __init__(self, file):
        self.file = file
        self.extensions = ", ".join(item.upper() for item in ALLOWED_EXTENSIONS)


class InvalidFileSizeError(Exception):
    """Occurs when a file does not conform to MAX_FILE_SIZE."""

    def __init__(self, file):
        self.file = file
        self.max_file_size = MAX_FILE_SIZE


class UploadHelper:
    def upload_file(self, directory, file):
        if not self.is_valid_type(file):
            raise InvalidFileTypeError(file)

        if not self.is_valid_size(file):
            raise InvalidFileSizeError(file)

        filename = enforce_secure_filename(file.filename)
        full_path = join(directory, filename)
        file.save(full_path)

        project = Project.find()
        return full_path.replace(f"{str(project.root)}/", "")

    def is_valid_type(self, file):
        return file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    def is_valid_size(self, file):
        # File size calculated due to multipart/form data (initial header content-length may differ when complete file data has been uploaded)
        file.seek(0, SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Return to 0 so subsequent write occurs from beginning of file
        return 0 < file_size <= MAX_FILE_SIZE
