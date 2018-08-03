from app import db
from .base import Base

class Project(Base):

  __tablename__ = 'project'
  name = db.Column(db.String(128), nullable=False)
  git_url = db.Column(db.String(), nullable=False)
  validated = db.Column(db.Boolean(), default=False)

  def __init__(self, name, git_url):
    self.name = name
    self.git_url = git_url

  def __repr__(self):
    return '<Project %r>' % (self.name)

class Settings(Base):

  __tablename__ = 'setting'

  settings = db.Column(db.JSON(), nullable=False, default={
    'connections': []
  })
  project_id = db.Column(db.Integer,
    db.ForeignKey('project.id'), nullable=False)
  project = db.relationship('Project',
    backref=db.backref('settings', lazy=True, uselist=False))

  def serializable(self):
    this_setting = {}
    this_setting['settings'] = self.settings

    return this_setting

  def __init__(self):
    super().__init__()
    
  def __repr__(self):
    return '<Measure %i>' % (self.id)