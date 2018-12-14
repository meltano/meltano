{
  sql_table_name = gitlab.region
  dimensions {
    id {
      primary_key = true
      hidden = true
      type = string
      sql = {{table}}.id
    }

    name {
      description = Carbon region long name
      type = string
      sql = {{table}}.dnoregion
    }

    short_name {
      description: Carbon region short name
      type: string
      sql: {{table}}.shortname
    }

    measure: count {
      description: Runner Count
      type: count
      sql: {{table}}.id
    }
  }
}