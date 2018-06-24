class SqlHelper():

  def get_func(self, t, table, sql):
    if t.lower() == 'sum':
      return self.sum(table, sql)

  def sum(self, table, sql):
    return 'COALESCE(SUM({}), 0) AS {}'.format(sql.replace('${TABLE}', table), sql.replace('${TABLE}.', ''))

  def group_by(self, dimensions, measures):
    if dimensions and measures:
      length = len(list(dimensions))
      return 'GROUP BY {}'.format(', '.join([str(x) for x in list(range(1,length+1))]))
    else:
      return ''