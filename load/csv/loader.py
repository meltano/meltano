import os

TEMP_FOLDER = 'static/tmp'


class CsvLoader:
    def __init__(self, **kwargs):
        self.extractor = kwargs['extractor']

    def schema_apply(self):
        print("No need to apply schema for csv ")
        pass

    def load(self, df, schema_name):
        print(f'Saving file for schema: {schema_name}')
        file_name = os.path.join(TEMP_FOLDER, f'{self.extractor.name}_{schema_name}.csv')
        with open(file_name, 'a') as csv_file:
            if not df.empty:
                df.to_csv(path_or_buf=csv_file, index=False)
                return file_name
            else:
                print(f'DataFrame {df} is empty -> skipping it')
