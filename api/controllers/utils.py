import re
from sqlalchemy import String, cast
from .substitution import Substitution
from .aggregate import Aggregate
from models.data import View, Dimension, DimensionGroup, Measure, Join
from pypika import Query, Table, Field

class SqlHelper():

  def parse_sql(self, input):
    placeholders = self.placeholder_match(input)

  def placeholder_match(self, input):
    outer_pattern = r'(\$\{[\w\.]*\})'
    inner_pattern = r'\$\{([\w\.]*)\}'
    outer_results = re.findall(outer_pattern, input);
    inner_results = re.findall(inner_pattern, input);
    return (outer_results, inner_results)

  def get_sql(self, explore, incoming_json):
    view_name = incoming_json['view']
    view = View.query.filter(View.name == view_name).first()
    base_table = view.settings['sql_table_name']
    (schema, table) = base_table.split('.')
    incoming_dimensions = incoming_json['dimensions']
    incoming_dimension_groups = incoming_json['dimension_groups']
    incoming_measures = incoming_json['measures']
    incoming_filters = incoming_json['filters']
    # get all timeframes
    timeframes = [t['timeframes'] for t in incoming_dimension_groups]
    # flatten list of timeframes
    timeframes = [y for x in timeframes for y in x]
    dimensions = list(filter(lambda x: x.name in incoming_dimensions, view.dimensions))
    measures = list(filter(lambda x: x.name in incoming_measures, view.measures))
    table = self.table(base_table, explore.name)
    dimensions = self.dimensions(dimensions, table)
    measures = self.measures(measures, table)
    return self.get_query(from_=table, dimensions=dimensions, measures=measures)


  def table(self, name, alias):
    (schema, name) = name.split('.')
    return Table(name, schema=schema, alias=alias)

  def dimensions(self, dimensions, table):
    return [self.field_from_dimension(d, table) for d in dimensions]

  def field_from_dimension(self, d, table):
    sql = d.settings['sql']
    substitution = Substitution(sql, table, dimension=d)
    return substitution.sql

  def measures(self, measures, table):
    return [self.field_from_measure(m, table) for m in measures]

  def field_from_measure(self, m, table):
    aggregate = Aggregate(m, table)
    return aggregate.sql

  def get_query(self, from_, dimensions, measures):
    select = dimensions + measures
    q = Query.from_(from_).select(*select).groupby(*dimensions)
    return '{};'.format(str(q))