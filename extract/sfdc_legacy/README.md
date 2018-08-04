### Adding fields
To add fields, update the `sfdc_manifest.yaml` file. Note that the attribute name should be lowercased. The schema should be automatically updated on the next run.

If you're updating the opportunity object, you need to also update the schema in the `sfdc_derived.ss_opportunity` object and add the line to `util/snapshot.py`.