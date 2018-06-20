from app import db
from .base import Base

class BaseLook(Base):
  __abstract__  = True
  name = db.Column(db.String(128), nullable=False)
  settings = db.Column(db.JSON(), nullable=True)

  def __init__(self, name, settings):
    self.name = name
    self.settings = settings

class Model(BaseLook):

  __tablename__ = 'model'

  def __init__(self, name, settings):
    super().__init__(name, settings)

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
    lazy='dynamic',
    back_populates="explores")
  joins = db.relationship('Join',
    backref='explore',
    lazy=True)

  def __init__(self, name, settings):
    super().__init__(name, settings)

  def __repr__(self):
    return '<Explore %i>' % (self.id)

  def serializable(self, include_dimensions_and_measures=False):
    this_explore = {}
    this_explore['settings'] = self.settings
    this_explore['name'] = self.name
    this_explore_model = {}
    this_explore_model['settings'] = self.model.settings
    this_explore_model['name'] = self.model.name
    this_explore['model'] = this_explore_model
    this_explore['views'] = []
    this_explore['joins'] = []
    this_explore['unique_name'] = 'explore_{}'.format(self.name)
    for view in self.views:
      this_view = {}
      this_view['name'] = view.name
      this_view['settings'] = view.settings
      this_view['unique_name'] = 'view_{}'.format(view.name)
      this_view['collapsed'] = True
      if include_dimensions_and_measures:
        this_view['dimensions'] = []
        for dimension in view.dimensions:
          this_dimension = {}
          this_dimension['name'] = dimension.name
          this_dimension['settings'] = dimension.settings
          this_dimension['unique_name'] = 'dimension_{}'.format(dimension.name)
          this_view['dimensions'].append(this_dimension)

        this_view['measures'] = []
        for measure in view.measures:
          this_measure = {}
          this_measure['name'] = measure.name
          this_measure['settings'] = measure.settings
          this_measure['unique_name'] = 'measure_{}'.format(measure.name)
          this_view['measures'].append(this_measure)
      this_explore['views'].append(this_view)
    for join in self.joins:
      this_join = {}
      this_join['name'] = join.name
      this_join['settings'] = join.settings
      this_explore['joins'].append(this_join)
    return this_explore

class Join(BaseLook):
  __tablename__ = 'join'

  explore_id = db.Column(db.Integer,
    db.ForeignKey('explore.id'),
    nullable=False)

  def __init__(self, name, settings):
    super().__init__(name, settings)

class View(BaseLook):

  __tablename__ = 'view'

  explores = db.relationship(
    "Explore",
    secondary=explore_view,
    lazy='dynamic',
    back_populates="views")

  def __init__(self, name, settings):
    super().__init__(name, settings)

  def __repr__(self):
    return '<View %i>' % (self.id)

class Dimension(BaseLook):

  __tablename__ = 'dimension'

  view_id = db.Column(db.Integer,
    db.ForeignKey('view.id'), nullable=False)
  view = db.relationship('View',
    backref=db.backref('dimensions', lazy=True))

  def __init__(self, name, settings):
    super().__init__(name, settings)
    
  def __repr__(self):
    return '<Dimension %i>' % (self.id)

class Measure(BaseLook):

  __tablename__ = 'measure'

  view_id = db.Column(db.Integer,
    db.ForeignKey('view.id'), nullable=False)
  view = db.relationship('View',
    backref=db.backref('measures', lazy=True))

  def __init__(self, name, settings):
    super().__init__(name, settings)
    
  def __repr__(self):
    return '<Measure %i>' % (self.id)