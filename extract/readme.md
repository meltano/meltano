`extract` folder holds extractors which are used in the Meltano tool. 


Structure of the `extract` folder is used to discover Extractors available to the tool:
 - Folder name capitalized
 - Folder name is used to find the name of the extractor in that folder. 
`EXTRACTOR_MODULE_NAME_PATTERN = f'extract.{folder_name}.{folder_name}Extractor'`
Example: for folder named `Demo` Meltano expects a `DemoExtractor` class to be importable from the `Demo` folder.    
