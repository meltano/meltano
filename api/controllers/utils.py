import re
from sqlalchemy import String, cast
from models.data import View, Dimension, Measure, Join

class SqlHelper():

  def get_func(self, t, table, sql):
    if t.lower() == 'sum':
      return self.sum(table, sql)
    if t.lower() == 'count':
      return self.count(table, sql)

  def sum(self, table, sql):
    table_name = sql.replace('${TABLE}', table)
    return 'COALESCE(SUM({}), 0) AS "{}"'.format(table_name, sql.replace('${TABLE}', table))

  def count(self, table, sql):
    primary_key = Dimension.query\
      .join(View, Dimension.view_id == View.id)\
      .filter(cast(Dimension.settings["primary_key"], String) == 'true')\
      .filter(View.name == table)\
      .first()
    
    table_name = primary_key.settings['sql'].replace('${TABLE}', primary_key.view.name)
    return 'COUNT(DISTINCT {}) AS "{}.count"'\
      .format(table_name, primary_key.view.name)

  def group_by(self, joins, dimensions):
    length = 0
    if joins or dimensions:
      if joins:
        for join in joins:
          if 'dimensions' in join:
            length = length + len(join['dimensions'])
      elif dimensions:
        length = len(list(dimensions))
      return 'GROUP BY {}'.format(', '.join([str(x) for x in list(range(1,length+1))]))
    else:
      return ''

  def join_dimensions(self, joins):
    if len(joins):
      dimensions = []
      for join in joins:
        if 'dimensions' in join:
          queried_dimensions = Dimension.query\
            .join(View, Dimension.view_id == View.id)\
            .filter(View.name == join['name'])\
            .filter(Dimension.name.in_(join['dimensions'])).all()
          
          for dimension in queried_dimensions:
            table_and_column = dimension.table_column_name
            dimensions.append('{} AS "{}"'.format(table_and_column, table_and_column))
      if len(dimensions):
        return ",\n\t ".join(dimensions)
    return None

  def join_measures(self, joins):
    if len(joins):
      measures = []
      for join in joins:
        if 'measures' in join:
          queried_measures = Measure.query\
            .join(View, Measure.view_id == View.id)\
            .filter(View.name == join['name'])\
            .filter(Measure.name.in_(join['measures'])).all()
          
          for measure in queried_measures:
            sql = measure.settings['sql'] if 'sql' in measure.settings else None
            measures.append(self.get_func(measure.settings['type'], join['name'], sql))
      if len(measures):
        return ",\n\t ".join(measures)
    return None

  def join_type(self, join):
    if not 'type' in join.settings:
      return 'LEFT JOIN'
    else:
      type_of_join = join.settings['type'].lower()
      if type_of_join == 'inner':
        return 'INNER JOIN'
      elif type_of_join == 'full_outer':
        return 'FULL OUTER JOIN'
      elif type_of_join == 'cross':
        return 'CROSS JOIN'

  def join_sql(self, join, view):
    outer_pattern = r'(\$\{[\w\.]*\})'
    inner_pattern = r'\$\{([\w\.]*)\}'
    sql = join.settings['sql_on']
    outer_results = re.findall(outer_pattern, sql);
    inner_results = re.findall(inner_pattern, sql);
    related_view = View.query.filter(View.name == join.name).first()

    def dimension_actual_name(result):
      (joined_view, joined_dimension) = result.split('.')
      queried_view = view

      if view.name != joined_view:
        queried_view = related_view
      
      queried_dimension = Dimension.query\
        .join(View, Dimension.view_id == View.id)\
        .filter(Dimension.name == joined_dimension)\
        .filter(View.id == queried_view.id)\
        .first()

      return queried_dimension.table_column_name

    inner_results = list(map(dimension_actual_name, inner_results))

    for i, result in enumerate(outer_results):
      sql = sql.replace(result, inner_results[i])

    return '{} AS {} ON {}'.format(related_view.settings['sql_table_name'], join.name, sql)

  def joins_by(self, joins, view):
    joins_sql = []
    if len(joins):
      for join in joins:
        queried_join = Join.query\
          .filter(Join.name == join['name'])\
          .first()
        join_type = self.join_type(queried_join)
        join_sql = self.join_sql(queried_join, view)
        joins_sql.append(' '.join([join_type, join_sql]))
    return '\n'.join(joins_sql)

  def filter_by(self, filter_by, table):
    base_sqls = [];
    for key, val in filter_by.items():
      modifier = ''
      if 'modifier' not in val:
        modifier = 'equal'
      else:
        modifier = val['modifier']
      
      table_name = key.replace('${TABLE}', table)
      selections = []
      if 'selections' in val:
        selections = val['selections']
      
      if not len(selections) and modifier != 'isnull':
        continue
      
      is_single = len(selections) == 1 
      base_sql = ''
      if modifier == 'equal':
        if is_single:
          base_sql = "({} = '{}')".format(table_name, selections[0])
        else:
          selections = ["'{}'".format(selection) for selection in selections]
          fields = ', '.join(selections)
          base_sql = '(({} IN ({})))'.format(table_name, fields)
      elif modifier == 'contains':
        if is_single:
          base_sql = "({} LIKE '%{}%')".format(table_name, selections[0])
        else:
          base_sql = " OR ".join(["{} LIKE '%{}%'".format(table_name, selection) for selection in selections])
          base_sql = "({})".format(base_sql)
      elif modifier == 'startswith':
        if is_single:
          base_sql = "({} LIKE '{}%')".format(table_name, selections[0])
        else:
          base_sql = " OR ".join(["{} LIKE '{}%'".format(table_name, selection) for selection in selections])
          base_sql = "({})".format(base_sql)
      elif modifier == 'endswith':
        if is_single:
          base_sql = "({} LIKE '%{}')".format(table_name, selections[0])
        else:
          base_sql = " OR ".join(["{} LIKE '%{}'".format(table_name, selection) for selection in selections])
          base_sql = "({})".format(base_sql)
      elif modifier == 'isblank':
        base_sql = "(({} IS NULL OR LENGTH({}) = 0))".format(table_name, table_name)
      elif modifier == 'isnull':
        base_sql = "(({} IS NULL))".format(table_name)
      base_sqls.append(base_sql)
    if not len(base_sqls):
      return ''
    return 'WHERE {}'.format(' \n\tAND\n\t '.join(base_sqls))