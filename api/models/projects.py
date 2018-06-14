from app import db
from .base import Base

class Project(Base):

  __tablename__ = 'project'
  name = db.Column(db.String(128),  nullable=False)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return '<Project %r>' % (self.name)