from elt.schema import Schema, Column, DBType


PG_SCHEMA = 'zendesk'
PG_TABLE = 'tickets'
PRIMARY_KEY = 'id' # TODO: confirm


def describe_schema(args) -> Schema:
    table_name = args.table_name or PG_TABLE
    table_schema = args.schema or PG_SCHEMA

    # curry the Column object
    def column(column_name, data_type, *,
               is_nullable=True,
               is_mapping_key=False):
        return Column(table_schema=table_schema,
                      table_name=table_name,
                      column_name=column_name,
                      data_type=data_type.value,
                      is_nullable=is_nullable,
                      is_mapping_key=is_mapping_key)

    return Schema(table_schema, [
        column("id",                     DBType.Long, is_mapping_key=True),
        column("url",                    DBType.String),
        column("external_id",            DBType.String, is_mapping_key=True),
        column("type",                   DBType.String),
        column("subject",                DBType.String),
        column("raw_subject",            DBType.String),
        column("description",            DBType.String),
        column("priority",               DBType.String),
        column("status",                 DBType.String),
        column("recipient",              DBType.String),
        column("requester_id",           DBType.Long, is_nullable=False),
        column("submitter_id",           DBType.Long),
        column("assignee_id",            DBType.Long),
        column("organization_id",        DBType.Long),
        column("group_id",               DBType.Long),
        column("collaborator_ids",       DBType.ArrayOfLong),
        column("collaborators",          DBType.ArrayOfString),
        column("follower_ids",           DBType.ArrayOfLong),
        column("forum_topic_id",         DBType.Long),
        column("problem_id",             DBType.Long),
        column("has_incidents",          DBType.Boolean),
        column("due_at",                 DBType.Date),
        column("tags",                   DBType.ArrayOfString),
        column("via",                    DBType.JSON),
        column("custom_fields",          DBType.JSON),
        column("satisfaction_rating",    DBType.JSON),
        column("sharing_agreement_ids",  DBType.ArrayOfLong),
        column("followup_ids",           DBType.ArrayOfLong),
        column("email_cc_ids",           DBType.ArrayOfLong),
        column("via_followup_source_id", DBType.Long),
        column("macro_ids",              DBType.ArrayOfLong),
        column("ticket_form_id",         DBType.Long),
        column("brand_id",               DBType.Long),
        column("allow_channelback",      DBType.Boolean),
        column("is_public",              DBType.Boolean),
        column("created_at",             DBType.Date),
        column("updated_at",             DBType.Date),
        column("generated_timestamp",    DBType.Long),
        column("fields",                 DBType.JSON),
    ])


def table_name(args):
    return args.table_name or PG_TABLE
