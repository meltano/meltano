import mkto_tools.mkto_leads
import mkto_tools.mkto_activities

from elt.cli import OptionEnum


class MarketoSource(OptionEnum):
    LEADS = "leads"
    ACTIVITIES = "activities"


class ExportType(OptionEnum):
    CREATED = "created"
    UPDATED = "updated"


class MarketoSource(OptionEnum):
    LEADS = "leads"
    ACTIVITIES = "activities"


def config_table_name(args):
    table_name_source_map = {
        MarketoSource.LEADS: mkto_tools.mkto_leads.PG_TABLE,
        MarketoSource.ACTIVITIES: mkto_tools.mkto_activities.PG_TABLE,
    }

    return args.table_name or table_name_source_map[args.source]


def config_primary_key(args):
    pkey_source_map = {
        MarketoSource.LEADS: mkto_tools.mkto_leads.PRIMARY_KEY,
        MarketoSource.ACTIVITIES: mkto_tools.mkto_activities.PRIMARY_KEY,
    }

    return pkey_source_map[args.source]

def config_integrate(args):
    return {
        'table_schema': args.schema,
        'table_name': config_table_name(args),
        'primary_key': config_primary_key(args),
        'csv_options': { 'NULL': "'null'" }
    }
