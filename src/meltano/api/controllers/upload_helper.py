from os.path import join

from werkzeug.utils import secure_filename

from meltano.core.project import Project


class UploadHelper:

    def upload_file(self, directory, file):
        project = Project.find()
        filename = secure_filename(file.filename)
        file.save(join(project.extract_dir(directory), filename))