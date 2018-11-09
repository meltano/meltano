import os


class CsvLoader:
    def __init__(self, **kwargs):
        TEMP_FOLDER = "/tmp"
        self.extractor = kwargs["extractor"]
        self.entity_name = kwargs["entity_name"]
        if "output_path" in kwargs:
            output_path = kwargs["output_path"]
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            self.output_path = output_path
        else:
            if not os.path.exists(TEMP_FOLDER):
                os.makedirs(TEMP_FOLDER)
            self.output_path = TEMP_FOLDER

    def schema_apply(self):
        """
        The schema apply is set to run once per entity before the extract phase
          in order to initialize the target of the load operation.

        In the case of csv files, we want to delete the tmp csv files from
          older extraction runs, otherwise the new data would be appended to
          the data from the previous execution.
        """
        # print(f'Deleting existing csv files for {self.entity_name}')
        file_name = f"{self.extractor.name}--{self.entity_name}.csv"
        file_path = os.path.join(self.output_path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    def load(self, df):
        print(f"Updating csv file for entity: {self.entity_name}")
        file_name = f"{self.extractor.name}--{self.entity_name}.csv"
        file_path = os.path.join(self.output_path, file_name)
        with open(file_path, "a") as csv_file:
            if not df.empty:
                write_header: bool = file_is_empty(file_path)
                df.to_csv(path_or_buf=csv_file, index=False, header=write_header)
                return file_name
            else:
                print(f"DataFrame {df} is empty -> skipping it")


def file_is_empty(path):
    return os.stat(path).st_size == 0
