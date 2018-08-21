from app import db
from models.base import Base

POSTGRES_CONNECT_VALUES = {
    "dev_dw": {
        "type": "postgres",
        "threads": 2,
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "pass": "pass",
        "dbname": "dw",
        "schema": "dev"}
}


class Settings(Base):
    __tablename__ = 'settings'
    settings = db.Column(db.JSON(), nullable=False, default={'connections': POSTGRES_CONNECT_VALUES})
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref=db.backref('settings', lazy=True, uselist=False))

    def serializable(self):
        return {'settings': self.settings}

    def __repr__(self):
        return f'<Settings for {self.project} id: {self.id}>'
