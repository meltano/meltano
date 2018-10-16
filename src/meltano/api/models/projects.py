from ..app import db
from ..models.base import Base


class Project(Base):
    __tablename__ = "project"
    name = db.Column(db.String(128), nullable=False)
    git_url = db.Column(db.String(), nullable=False)
    validated = db.Column(db.Boolean(), default=False)

    def __init__(self, name, git_url):
        self.name = name
        self.git_url = git_url

    def __repr__(self):
        return f"<Project {self.name}>"
