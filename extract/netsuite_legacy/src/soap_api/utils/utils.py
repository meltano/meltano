import json


def fetch_attribute(parent_entity, record, column_map):
    """
    Given a record and a column mapping, fetch the data for the attribute defined in the mapping

    column_map = {
      'in': attribute name as found in the record,
      'out': attribute name used as a template for the returned dictionary,
      'type': the type of the attribute. Either a simple type or more
            complex types relevant to this Entity
    }

    Extracting data based on a column_map could result to multiple entries
     e.g. in case of an address or other nested structures

    The parent_enity is the entity for wich we fetch the attribute.
    Used for fetching the schema of related
     entities (from RELATED_ENTITIES) if a nested related entity is requested.

    In case of nested attributes (defined with the 'ENTITY_LIST' type), we want
     to also extract the data and store them in the related entity's table.
    So, during the extraction of data from such types we may also get back
      {entity: ENTITY_CLASS, data: Extracted_Records} dictionaries.
    Those are stored in the related_entities and returned back to the caller of
      fetch_attribute() for further processing.

    TL;DR: Extracting a single attribute's value could result in multiple
            records inserted in a related table.
           Example: A transaction may have 20 transaction lines stored as a
            nested structure with additional information and an array of lines.
           We want those trans lines; not as JSON but as separate entries in a table.

    Returns a dictionary with the related_entities and the attributes to be
     added to the parent Entity:
     {'attributes': dict of attribute:values,
      'related_entities': [ {'entity': , data:} ] }
    """
    related_entities = []
    result = {}

    # Simple Data types that can be trivially extracted with minimal effort
    if  column_map['type'] == 'Integer' \
      or column_map['type'] == 'Long' \
      or column_map['type'] == 'Double' \
      or column_map['type'] == 'Boolean' \
      or column_map['type'] == 'String':
        if column_map['in'] in record:
            result[ column_map['out'] ] = record[ column_map['in'] ]
        else:
            result[ column_map['out'] ] = None

    elif  column_map['type'] == 'Timestamp':
        if column_map['in'] in record and record[ column_map['in'] ] is not None:
            result[ column_map['out'] ] = record[ column_map['in'] ].isoformat()
        else:
            result[ column_map['out'] ] = None

    elif  column_map['type'] == 'JSON':
        result[ column_map['out'] ] = json.dumps(record[ column_map['in'] ])

    elif  column_map['type'] == 'JSON_MANUAL':
        # Do Nothing --> We'll manually curate and import the JSON
        #  attributes in the transform function
        result[ column_map['out'] ] = None

    # Complex Types specific to NetSuite
    elif  column_map['type'] == 'ENTITY_LIST_AS_JSON':
        # only fetch the support entity's records and store them as Json
        result[ column_map['out'] ] = fetch_entity_list_as_json(parent_entity, record, column_map['in'])

    elif  column_map['type'] == 'ENTITY_LIST':
        # fetch the support entity's records
        transform_results = fetch_entity_list(parent_entity, record, column_map['in'])

        if transform_results is None or len(transform_results) == 0:
            result[ column_map['out'] ] = None
        else:
            # add them to the related entities list so that they are:
            #  returned back to the transform operation
            #  --> sent back to the exporter when everything is finished
            #  --> and finally properly imported by the importer
            related_entities.extend(transform_results)

            # Also store them as JSON in the parent Entity's table for reference
            entity_list_records = transform_results[0]['data']

            # This is going to be used in JSON, so throw away attributes with none values
            #tmp_field = {k: v for k, v in tmp_field.items() if v is not None}

            # store them as Json
            result[ column_map['out'] ] = json.dumps(entity_list_records)


    elif  column_map['type'] == 'RecordRef':
        if column_map['in'] in record and record[ column_map['in'] ] is not None:
            result[column_map['out'] + '_id'] = record[ column_map['in'] ]['internalId']
            result[column_map['out'] + '_name'] = record[ column_map['in'] ]['name']
        else:
            result[column_map['out'] + '_id'] = None
            result[column_map['out'] + '_name'] = None

    elif  column_map['type'] == 'Address':
        if column_map['in'] in record and record[column_map['in']] is not None:
            result[column_map['out'] + "_id"] = record[column_map['in']]['internalId']
            result[column_map['out'] + "_country"] = record[column_map['in']]['country']
            result[column_map['out'] + "_addressee"] = record[column_map['in']]['addressee']
            result[column_map['out'] + "_addr_phone"] = record[column_map['in']]['addrPhone']
            result[column_map['out'] + "_addr1"] = record[column_map['in']]['addr1']
            result[column_map['out'] + "_addr2"] = record[column_map['in']]['addr2']
            result[column_map['out'] + "_addr3"] = record[column_map['in']]['addr3']
            result[column_map['out'] + "_city"] = record[column_map['in']]['city']
            result[column_map['out'] + "_state"] = record[column_map['in']]['state']
            result[column_map['out'] + "_zip"] = record[column_map['in']]['zip']
            result[column_map['out'] + "_addr_text"] = record[column_map['in']]['addrText']
            result[column_map['out'] + "_override"] = record[column_map['in']]['override']
        else:
            result[column_map['out'] + "_id"] = None
            result[column_map['out'] + "_country"] = None
            result[column_map['out'] + "_addressee"] = None
            result[column_map['out'] + "_addr_phone"] = None
            result[column_map['out'] + "_addr1"] = None
            result[column_map['out'] + "_addr2"] = None
            result[column_map['out'] + "_addr3"] = None
            result[column_map['out'] + "_city"] = None
            result[column_map['out'] + "_state"] = None
            result[column_map['out'] + "_zip"] = None
            result[column_map['out'] + "_addr_text"] = None
            result[column_map['out'] + "_override"] = None

    elif  column_map['type'] == 'SubCurrency':
        if column_map['in'] in record and record[ column_map['in'] ] is not None:
            result[ column_map['out'] ] = record[ column_map['in'] ]['internalId']
        else:
            result[ column_map['out'] ] = None

    elif  column_map['type'] == 'RecordRefList':
        if column_map['in'] in record and record[column_map['in']] is not None \
          and record[column_map['in']]['recordRef'] is not None :
            recordRefList = []

            for record_entry in record[column_map['in']]['recordRef']:
                tmp_field = {
                    "internalId": record_entry['internalId'],
                    "name": record_entry['name'],
                }

                recordRefList.append(tmp_field)

            result[ column_map['out'] ] = json.dumps(recordRefList)
        else:
            result[ column_map['out'] ] = None

    elif  column_map['type'] == 'CustomFieldList':
        if column_map['in'] in record and record[column_map['in']] is not None \
          and record[column_map['in']]['customField'] is not None :
            customFieldList = []

            for record_entry in record[column_map['in']]['customField']:
                tmp_field = {
                    "internalId": record_entry['internalId'],
                    "scriptId": record_entry['scriptId'],
                }

                if 'value' in record_entry and record_entry['value'] is not None:
                    if type(record_entry['value']) in (int, float, bool, str):
                        tmp_field["value"] = record_entry['value']
                    elif 'internalId' in record_entry['value']:
                        tmp_field["value"] = {
                            "name": record_entry['value']['name'],
                            "internalId": record_entry['value']['internalId'],
                            "typeId": record_entry['value']['typeId'],
                        }

                customFieldList.append(tmp_field)

            result[ column_map['out'] ] = json.dumps(customFieldList)
        else:
            result[ column_map['out'] ] = None

    return {'attributes': result, 'related_entities': related_entities}


def fetch_entity_list(parent_entity, record, entity_name):
    """
    Extract a full list of entities (entity_name) from a record

    The way NetSuite stores such entities is:
        'entity_name': {
            'node_name': [  <--- Can use multiple names here depending on type
                          { entity 1} , { entity 2} , ....
                         ]
    But we want to treat all similar entities (e.g. expense lists) in the same way
    So we have to also set multiple node names in the RELATED_ENTITIES dictionary
     and check which is the one provided for this record

    The parent entity (the one the record is for) is used in order
     to have access to the RELATED_ENTITIES dictionary (different for each major entity)
    """
    if entity_name in record and record[entity_name] is not None \
      and entity_name in parent_entity.schema.RELATED_ENTITIES:
        node_name = None

        # Find the node name under which the data are stored
        for name in parent_entity.schema.RELATED_ENTITIES[entity_name]['node_names']:
            if record[entity_name][name] is not None:
                # found the node name used in this iteration
                node_name = name
                break;

        if node_name is None:
            return None

        # Find this entity's class name and create an instance
        class_name = parent_entity.schema.RELATED_ENTITIES[entity_name]['class_name']
        entity_class = parent_entity.client.supported_entity_class_factory(class_name)

        if entity_class is None:
            return None

        enity = entity_class()

        # Return the result of transforming the provided record node
        return enity.transform(records=record[entity_name][node_name],
                               parent_id=record['internalId'])
    else:
        return None


def merge_transform_results(list1, list2):
    """
    Merge transform results list2 in list1

    Both are lists with transform results, e.g.
     [{'entity': Transaction, 'data': records}, {'entity': Currency, 'data': records}, ... ]

    The issue solved is that while extracting a batch of transactions we may have 100s
     of support entity lists. For example while fetching a batch of 100 Transactions
     we may have close to 100 Expense lists, each with its expense lines stored inside.

    The result is that in each iteration we may have to create 1 + 100 files and import
     them seperatelly. This merge step makes sure that if we have to create only one file
     per support entity, per batch.
    """
    for tr in list2:
        index = next((indx for (indx, d) in enumerate(list1) if d["entity"] == tr['entity']), None)
        if index is None:
            list1.append(tr)
        else:
            list1[index]['data'].extend(tr['data'])


def fetch_entity_list_as_json(parent_entity, record, entity_name):
    """
    Extract a full list of entities (entity_name) from a record

    The way NetSuite stores such entities is:
        'entity_name': {
            'node_name': [  <--- Can use multiple names here depending on type
                          { entity 1} , { entity 2} , ....
                         ]
    But we want to treat all similar entities (e.g. expense lists) in the same way
    So we have to also set multiple node names in the RELATED_ENTITIES dictionary
     and check which is the one provided for this record

    The parent entity (the one the record is for) is used in order
     to have access to the RELATED_ENTITIES dictionary (different for each major entity)
    """
    if entity_name in record and record[entity_name] is not None \
      and entity_name in parent_entity.schema.RELATED_ENTITIES:
        node_name = None

        for name in parent_entity.schema.RELATED_ENTITIES[entity_name]['node_names']:
            if record[entity_name][name] is not None:
                # found the node name used in this iteration
                node_name = name
                break;

        if node_name is not None:
            entity_list = []

            for record_entry in record[entity_name][node_name]:
                tmp_field = {}

                for column_map in parent_entity.schema.RELATED_ENTITIES[entity_name]['column_map']:
                    # recursivelly create a record for each entry by using the map for this entity
                    extraction_result = fetch_attribute(parent_entity, record_entry, column_map)

                    tmp_field.update( extraction_result['attributes'] )

                # This is going to be used in JSON, so throw away attributes with none values
                tmp_field = {k: v for k, v in tmp_field.items() if v is not None}

                entity_list.append(tmp_field)

            return json.dumps(entity_list)
        else:
            return None
    else:
        return None
