# from enum import Enum
# from .substitution import Substitution

# class JoinType(Enum):
#   left_join = 'left'
#   inner_join = 'inner'
#   full_outer_join = 'full_outer'
#   cross_join = 'cross'

# class Join():
#   def __init__(self, join, view, table):
#     self.fields = fields
#     self.table = table
#     self.sql = None
#     self.view = view
#     join_type = self.get_join_type(join)
#     join_sql = self.join_sql(join, table)
#     joins_sql.append(' '.join([join_type, join_sql]))
#     return '\n'.join(joins_sql)

#   def get_join_type(self, join)
#     if not 'type' in join.settings:
#       return JoinType.left_join
#     else:
#       type_of_join = join.settings['type'].lower()
#       if type_of_join == 'inner':
#         return JoinType.inner_join
#       elif type_of_join == 'full_outer':
#         return JoinType.full_outer_join
#       elif type_of_join == 'cross':
#         return JoinType.cross_join

#   def join_sql(self, join, view):
#     sql = join.settings['sql_on']
#     results = Substitution.placeholder_match(sql)
#     related_view = View.query.filter(View.name == join.name).first()

#     def dimension_actual_name(result):
#       (joined_view, joined_dimension) = result.split('.')
#       queried_view = view

#       if view.name != joined_view:
#         queried_view = related_view

#       queried_dimension = Dimension.query\
#         .join(View, Dimension.view_id == View.id)\
#         .filter(Dimension.name == joined_dimension)\
#         .filter(View.id == queried_view.id)\
#         .first()

#       return queried_dimension.table_column_name

#     inner_results = list(map(dimension_actual_name, results.inner_results))

#     for i, result in enumerate(results.outer_results):
#       sql = sql.replace(result, inner_results[i])

#     print([related_view.setting['sql_table_name'], join.name, sql])
#     return '{} AS {} ON {}'.format(related_view.settings['sql_table_name'], join.name, sql)
