class SqlHelper():

  def get_func(self, t, table, sql):
    if t.lower() == 'sum':
      return self.sum(table, sql)

  def sum(self, table, sql):
    return 'COALESCE(SUM({}), 0) AS {}'.format(sql.replace('${TABLE}', table), sql.replace('${TABLE}.', ''))

  def group_by(self, dimensions):
    if dimensions:
      length = len(list(dimensions))
      return 'GROUP BY {}'.format(', '.join([str(x) for x in list(range(1,length+1))]))
    else:
      return ''

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
          base_sql = "(%{} LIKE '{}')".format(table_name, selections[0])
        else:
          base_sql = " OR ".join(["%{} LIKE '{}'".format(table_name, selection) for selection in selections])
          base_sql = "({})".format(base_sql)
      elif modifier == 'isblank':
        base_sql = "(({} IS NULL OR LENGTH({}) = 0))".format(table_name, table_name)
      elif modifier == 'isnull':
        base_sql = "(({} IS NULL))".format(table_name)
      base_sqls.append(base_sql)
    if not len(base_sqls):
      return ''
    return 'WHERE {}'.format(' AND '.join(base_sqls))