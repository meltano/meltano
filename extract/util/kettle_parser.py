# Extremely messy one-off script to help convert kettle fields to meltano format

from fire import Fire

def kettle_parser(path_to_xml: str) -> str:
    """
    Parse our sfdc kettle files into somewhat usable meltano-format strings
    """

    with open(path_to_xml, 'r') as file:
        dump_file = file.read()

    types = ['<type>', '</type>']
    fields = ['<field>', '</field>']
    drop_other_fields = [line.rstrip().lstrip()
                         for line in dump_file.split('\n')
                         if all(x in line for x in types)
                         or all(x in line for x in fields)]

    removed_tags = drop_other_fields.copy()
    for x in types + fields:
        removed_tags = [line.replace(x, '') for line in removed_tags]

    lower_cased = [x.lower() for x in removed_tags]

    # Map the types correctly
    type_dict = {'string': 'character varying',
                 'number': 'real'}
    converted_types = [type_dict.get(x, x) for x in lower_cased]

    paired_stuff = zip(*[converted_types[i::2] for i in range(2)])


    for pair in paired_stuff:
        print('{}: {}'.format(pair[0].lower(), pair[1]))

if __name__ == '__main__':
    Fire()
