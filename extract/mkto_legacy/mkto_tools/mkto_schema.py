from elt.schema import DBType


data_types_map = {
    "date": DBType.Date,
    "string": DBType.String,
    "phone": DBType.String,
    "text": DBType.String,
    "percent": DBType.Double,
    "integer": DBType.Integer,
    "boolean": DBType.Boolean,
    "lead_function": DBType.String,
    "email": DBType.String,
    "datetime": DBType.Timestamp,
    "currency": DBType.String,
    "reference": DBType.String,
    "url": DBType.String,
    "float": DBType.Double,
}


def data_type(mkto_type) -> DBType:
    """
    Convert Marketo data type to DBType.
    Default to DBType.String if no mapping is present.

    :mkto_type: Marketo data type (from API)
    """
    return data_types_map.get(mkto_type, DBType.String)
