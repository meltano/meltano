How to work with loaders:

 0) Get the loader class by its name
 1) Create 1 loader object per entity loader = LoaderClass(**config_kwargs)
 2) Apply this loaders schema loader.apply_schema()
 3) For df in entity_dfs -> loader.load(df)

```python
class Loader():
    def __init__(self, **kwargs):
        self.entity_name = kwargs['entity_name']

    def apply_schema(self):
        pass

    def load(self, df):
        df.to_sql()
        pass

```
