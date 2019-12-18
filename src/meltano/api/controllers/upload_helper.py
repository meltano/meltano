from os import SEEK_END
from os.path import join
from pathlib import Path
from werkzeug.utils import secure_filename

from meltano.core.project import Project

MAX_FILE_SIZE = 4_194_304  # 4MB max
ALLOWED_EXTENSIONS = {"json"}


class InvalidFileNameError(Exception):
    """Occurs when a file does not have a valid name."""

    def __init__(self, file):
        self.file = file


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

        if not self.is_valid_name(file):
            raise InvalidFileNameError(file)

        filename = secure_filename(file.filename)
        full_path = join(directory, filename)

        if not self.is_valid_size(full_path):
            raise InvalidFileSizeError(file)

        file.save(full_path)

        project = Project.find()
        return full_path.replace(f"{str(project.root)}/", "")

    def is_valid_name(self, file):
        return file.filename != ""

    def is_valid_type(self, file):
        return file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    def is_valid_size(self, file_path):
        file_size = Path(file_path).stat().st_size
        return file_size > 0 and file_size <= MAX_FILE_SIZE
