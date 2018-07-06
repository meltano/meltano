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

class Explore(BaseLook):

  __tablename__ = 'explore'

  model_id = db.Column(db.Integer,
    db.ForeignKey('model.id'), nullable=False)
  model = db.relationship('Model',
    backref=db.backref('explores', lazy=True))
  view_id = db.Column(db.Integer,
    db.ForeignKey('view.id'), nullable=False)
  view = db.relationship('View',
    backref=db.backref('explores', lazy=True))
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
    this_explore['joins'] = []
    this_explore['unique_name'] = 'explore_{}'.format(self.name)
    this_view = {}
    this_view['name'] = self.view.name
    this_view['settings'] = self.view.settings
    this_view['unique_name'] = 'view_{}'.format(self.view.name)
    this_view['collapsed'] = True
    if include_dimensions_and_measures:
      this_view['dimensions'] = []
      for dimension in self.view.dimensions:
        this_dimension = {}
        this_dimension['name'] = dimension.name
        this_dimension['settings'] = dimension.settings
        this_dimension['label'] = dimension.settings.get('label', ' '.join(dimension.name.split('_')).title())
        this_dimension['unique_name'] = 'dimension_{}'.format(dimension.name)
        this_dimension['selected'] = False
        this_view['dimensions'].append(this_dimension)

      this_view['measures'] = []
      for measure in self.view.measures:
        this_measure = {}
        this_measure['name'] = measure.name
        this_measure['label'] = measure.settings.get('label', ' '.join(measure.name.split('_')).title())
        this_measure['settings'] = measure.settings
        this_measure['unique_name'] = 'measure_{}'.format(measure.name)
        this_measure['selected'] = False
        this_view['measures'].append(this_measure)
      this_explore['view'] = this_view
    for join in self.joins:
      this_join = {}
      this_join['name'] = join.name
      this_join['collapsed'] = True
      this_join['dimensions'] = []
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

  def __init__(self, name, settings):
    super().__init__(name, settings)

  def __repr__(self):
    return '<View %i>' % (self.id)

  def serializable(self, include_dimensions_and_measures=False):
    this_view = {}
    this_view['name'] = self.name
    this_view['settings'] = self.settings
    this_view['dimensions'] = []
    for dimension in self.dimensions:
      this_dimension = {}
      this_dimension['name'] = dimension.name
      this_dimension['settings'] = dimension.settings
      this_dimension['label'] = dimension.settings.get('label', ' '.join(dimension.name.split('_')).title())
      this_dimension['unique_name'] = 'dimension_{}'.format(dimension.name)
      this_dimension['selected'] = False
      this_view['dimensions'].append(this_dimension)
    this_view['measures'] = []
    for measure in self.measures:
      this_measure = {}
      this_measure['name'] = measure.name
      this_measure['label'] = measure.settings.get('label', ' '.join(measure.name.split('_')).title())
      this_measure['settings'] = measure.settings
      this_measure['unique_name'] = 'measure_{}'.format(measure.name)
      this_measure['selected'] = False
      this_view['measures'].append(this_measure)
    return this_view

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