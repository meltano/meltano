import re
from collections import namedtuple
from enum import Enum
from pypika import Field, Case

class SubstitutionType(Enum):
  unknown = 'UNKNOWN'
  table = 'TABLE'
  dimension = 'DIMENSION'
  view_dimension = 'VIEW_DIMENSION'
  view_sql_table_name = 'VIEW_SQL_TABLE_NAME'

class Substitution():
  def __init__(self, _input, table, dimension=None):
    self.input = _input
    self.alias = None
    self.sql = None
    self.table = table

    if not dimension:
      self.type = 'string'
    else:
      self.type = dimension.settings['type']

    self.outer_pattern = r'(\$\{[\w\.]*\})'
    self.inner_pattern = r'\$\{([\w\.]*)\}'
    self.substitutionType = SubstitutionType.unknown
    self.getSubstitutionType()
    self.placeholders = self.placeholder_match()
    self.setSql()


  def getSubstitutionType(self):
    # trying guess the substitutionType in a cheap way
    if '.' in self.input and '${TABLE}' not in self.input:
      if 'SQL_TABLE_NAME' in self.input:
        self.substitutionType = SubstitutionType.view_sql_table_name
      else:
        self.substitutionType = SubstitutionType.view_dimension
    elif '${TABLE}' in self.input:
      self.substitutionType = SubstitutionType.table
    elif ' ' not in self.input:
      self.substitutionType = SubstitutionType.dimension
    else:
      self.substitutionType = SubstitutionType.unknown

  def placeholder_match(self):
    outer_results = re.findall(self.outer_pattern, self.input);
    inner_results = re.findall(self.inner_pattern, self.input);
    Results = namedtuple('Results', 'inner outer')
    return Results(inner=inner_results, outer=outer_results)

  def setSql(self):
    if self.substitutionType is SubstitutionType.table:
      self.setSqlTableType()
    else:
      raise Exception('Substitution Type {} not implemented yet'.format(self.substitutionType.value))

  def setSqlTableType(self):
    self.sql = self.input.replace(self.placeholders.outer[0], self.table._table_name)
    (table, field) = self.sql.split('.')
    self.alias = self.sql
    if self.type == 'yesno':
      field = Field(field, table=self.table)
      self.sql = Case(alias=self.sql)\
        .when(field, 'yes')\
        .else_('no')
    else:
      self.sql = Field(field, table=self.table, alias=self.sql)
