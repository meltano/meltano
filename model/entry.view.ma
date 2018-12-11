view "entry" {
  sql_table_name = gitlab.entry

  dimension {
    id {
      primary_key = yes
      hidden = yes
      type = string
      sql = {{TABLE}}.id
    }
    region_id {
      hidden = yes
      type = string
      sql = {{table}}.id
    }
  }
  dimension_group {
    from {
      description = Selected from range in carbon data
      type = time
      timeframes = [date, week, month, year]
      convert_tz = no
      sql = {{TABLE}}.from
    }
    to {
      description = Selected to range in carbon data
      type = time
      timeframes = [date, week, month, year]
      convert_tz = no
      sql = {{TABLE}}.to
    }
  }
}
