from app import db
from .base import Base

class BaseLook(Base):
  __abstract__  = True
  settings = db.Column(db.JSON(), nullable=True)

  def __init__(self, settings):
    self.settings = settings

class Model(BaseLook):

  __tablename__ = 'model'

  def __init__(self, settings):
    super().__init__(settings)

  def __repr__(self):
    return '<Model %i>' % (self.id)

explore_view = db.Table('explore_view',
    db.Column('explore_id', db.Integer, db.ForeignKey('explore.id'), primary_key=True),
    db.Column('view_id', db.Integer, db.ForeignKey('view.id'), primary_key=True)
)

class Explore(BaseLook):

  __tablename__ = 'explore'

  model_id = db.Column(db.Integer,
    db.ForeignKey('model.id'), nullable=False)
  model = db.relationship('Model',
    backref=db.backref('explores', lazy=True))
  views = db.relationship(
    "View",
    secondary=explore_view,
    back_populates="explores")

  def __init__(self, settings):
    super().__init__(settings)

  def __repr__(self):
    return '<Explore %i>' % (self.id)

class View(BaseLook):

  __tablename__ = 'view'
  explores = db.relationship(
    "Explore",
    secondary=explore_view,
    back_populates="views")

  def __init__(self, settings):
    super().__init__(settings)

  def __repr__(self):
    return '<View %i>' % (self.id)

class Dimension(BaseLook):

  __tablename__ = 'dimension'

  view_id = db.Column(db.Integer,
    db.ForeignKey('view.id'), nullable=False)
  view = db.relationship('View',
    backref=db.backref('dimensions', lazy=True))

  def __init__(self, settings):
    super().__init__(settings)
    
  def __repr__(self):
    return '<Dimension %i>' % (self.id)

class Measure(BaseLook):

  __tablename__ = 'measure'

  view_id = db.Column(db.Integer,
    db.ForeignKey('view.id'), nullable=False)
  view = db.relationship('View',
    backref=db.backref('measures', lazy=True))

  def __init__(self, settings):
    super().__init__(settings)
    
  def __repr__(self):
    return '<Measure %i>' % (self.id)