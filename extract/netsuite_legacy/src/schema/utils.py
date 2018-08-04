from elt.schema import DBType

def columns_from_mappings(column, column_mappings):
    columns = []

    for column_map in column_mappings:
        if  column_map['type'] == 'Integer':
            columns.append( column(column_map['out'], DBType.Integer) )

        elif  column_map['type'] == 'Long':
            columns.append( column(column_map['out'], DBType.Long) )

        elif  column_map['type'] == 'Double':
            columns.append( column(column_map['out'], DBType.Double) )

        elif  column_map['type'] == 'Boolean':
            columns.append( column(column_map['out'], DBType.Boolean) )

        elif  column_map['type'] == 'String':
            columns.append( column(column_map['out'], DBType.String) )

        elif  column_map['type'] == 'Timestamp':
            columns.append( column(column_map['out'], DBType.Timestamp) )

        elif  column_map['type'] == 'Date':
            columns.append( column(column_map['out'], DBType.Date) )

        elif  column_map['type'] == 'JSON':
            columns.append( column(column_map['out'], DBType.JSON) )

        elif  column_map['type'] == 'JSON_MANUAL':
            # An attribute defined as JSON but that we'll manually extract it
            #  vs just doing a json.dumps
            columns.append( column(column_map['out'], DBType.JSON) )

        # Complex Types specific to NetSuite
        elif  column_map['type'] == 'ENTITY_LIST_AS_JSON':
            # A List of Support entities stored as JSON in the parent table
            columns.append( column(column_map['out'], DBType.JSON) )

        elif  column_map['type'] == 'ENTITY_LIST':
            # A List of Support entities that will be stored in a related table
            # Also stored as JSON in the parent table for reference
            columns.append( column(column_map['out'], DBType.JSON) )

        elif  column_map['type'] == 'CustomFieldList':
            columns.append( column(column_map['out'], DBType.JSON) )

        elif  column_map['type'] == 'RecordRefList':
            columns.append( column(column_map['out'], DBType.JSON) )

        elif  column_map['type'] == 'RecordRef':
            columns.append( column(column_map['out'] + '_id',   DBType.Long) )
            columns.append( column(column_map['out'] + '_name', DBType.String) )

        elif  column_map['type'] == 'Address':
            columns.append( column(column_map['out'] + '_id',         DBType.String) )
            columns.append( column(column_map['out'] + '_country',    DBType.String) )
            columns.append( column(column_map['out'] + '_state',      DBType.String) )
            columns.append( column(column_map['out'] + '_city',       DBType.String) )
            columns.append( column(column_map['out'] + '_addr1',      DBType.String) )
            columns.append( column(column_map['out'] + '_addr2',      DBType.String) )
            columns.append( column(column_map['out'] + '_addr3',      DBType.String) )
            columns.append( column(column_map['out'] + '_zip',        DBType.String) )
            columns.append( column(column_map['out'] + '_addressee',  DBType.String) )
            columns.append( column(column_map['out'] + '_addr_phone', DBType.String) )
            columns.append( column(column_map['out'] + '_addr_text',  DBType.String) )
            columns.append( column(column_map['out'] + '_override',   DBType.Boolean) )

        elif  column_map['type'] == 'SubCurrency':
            columns.append( column(column_map['out'], DBType.String) )

    return columns
