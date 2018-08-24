import logging
import re
import sqlalchemy
from flask import jsonify
from pypika import Query, Table, Field
from sqlalchemy import String, cast
from .substitution import Substitution
from .aggregate import Aggregate
from .date import Date
from .join import Join as JoinQuery

from models.data import View, Dimension, DimensionGroup, Measure, Join
from app import app, db
from models.settings import Settings
from models.projects import Project

class SqlHelper:

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
        incoming_joins = incoming_json['joins']
        incoming_limit = incoming_json['limit']
        # get all timeframes
        timeframes = [t['timeframes'] for t in incoming_dimension_groups]
        # flatten list of timeframes
        timeframes = [y for x in timeframes for y in x]
        dimensions = list(filter(lambda x: x.name in incoming_dimensions, view.dimensions))
        measures = list(filter(lambda x: x.name in incoming_measures, view.measures))
        table = self.table(base_table, explore.name)
        # joins = self.joins(incoming_joins, table)
        dimension_groups = self.dimension_groups(view_name, incoming_dimension_groups, table)
        dimensions = self.dimensions(dimensions, table)
        dimensions = dimensions + dimension_groups
        measures = self.measures(measures, table)
        return self.get_query(from_=table, dimensions=dimensions, measures=measures, limit=incoming_limit)

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

    def joins(self, joins, table):
        if len(joins):
            for join in joins:
                queried_join = Join.query \
                    .filter(Join.name == join['name']) \
                    .first()
                join = JoinQuery(queried_join, view, table)

    def dimension_groups(self, view_name, dimension_groups, table):
        fields = []
        for dimension_group in dimension_groups:
            dimension_group_queried = DimensionGroup.query \
                .join(View, DimensionGroup.view_id == View.id) \
                .filter(View.name == view_name) \
                .filter(DimensionGroup.name == dimension_group['name']) \
                .first()
            (_table, name) = dimension_group_queried.table_column_name.split('.')
            for timeframe in dimension_group['timeframes']:
                d = Date(timeframe, table, name)
                fields.append(d.sql)
        return fields

    def get_query(self, from_, dimensions, measures, limit):
        select = dimensions + measures
        q = Query.from_(from_).select(*select).groupby(*dimensions).limit(limit)
        return f'{str(q)};'

    @app.route("/drop_it_like_its_hot")
    def reset_db():
        try:
            Settings.__table__.drop(db.engine)
            Project.__table__.drop(db.engine)
            db.drop_all()
        except sqlalchemy.exc.OperationalError as err:
            logging.error("Failed drop database.")
        db.create_all()
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
        return jsonify({"dropped_it": "like_its_hot"})

