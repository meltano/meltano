{
  name: carbon
  # Postgres DB
  #connection = runners_db
  label = carbon intensity
  explores {
    region {
      #from = region
      label = region
      description = Region Carbon Intensity Data

      joins {
        entry {
            fields = [entry.from, entry.to]
            sql_on = "{{region.id}} = {{entry.region_id}}"
            relationship = one_to_one
        }
      }
    }
  }
}