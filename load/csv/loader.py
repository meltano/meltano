import os
from api.config import TEMP_FOLDER


class CsvLoader:
    def __init__(self, **kwargs):
        self.extractor = kwargs['extractor']
        self.entity_name = kwargs['entity_name']
        if 'output_path' in kwargs:
            output_path = kwargs['output_path']
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            self.output_path = output_path
        else:
            if not os.path.exists(TEMP_FOLDER):
                os.makedirs(TEMP_FOLDER)
            self.output_path = TEMP_FOLDER

    @staticmethod
    def schema_apply():
        print("No need to apply schema for csv ")
        pass

    def load(self, df, entity_name):
        print(f'Saving file for schema: {entity_name}')
        file_name = f'{self.extractor.name}--{entity_name}.csv'
        file_path = os.path.join(self.output_path, file_name)
        with open(file_path, 'a') as csv_file:
            if not df.empty:
                write_header: bool = file_is_empty(file_path)
                df.to_csv(path_or_buf=csv_file, index=False, header=write_header)
                return file_name
            else:
                print(f'DataFrame {df} is empty -> skipping it')


def file_is_empty(path):
    return os.stat(path).st_size == 0
