from functools import wraps
from meltano.core.project import Project, ProjectNotFound

def project_from_slug(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            project = Project.find_by_slug(kwargs['project_slug'])
        except ProjectNotFound as e:
            project = None
            return jsonify(
                {
                    "result": False,
                    "errors": [{"message": f"{kwargs['project_slug']} is not a Meltano project.", "file_name": "*"}],
                    "files": [],
                }
            )
        kwargs['project'] = project
        del kwargs['project_slug']
        return f(*args, **kwargs)
    return decorated_function