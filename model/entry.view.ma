{
  sql_table_name = gitlab.entry

  dimensions {
    id {
      primary_key = yes
      hidden = yes
      type = string
      sql = "{{table}}.id"
    }
    region_id {
      hidden = yes
      type = string
      sql = "{{table}}.id"
    }
  }
  dimension_groups {
    from {
      description = Selected from range in carbon data
      type = time
      timeframes = [date, week, month, year]
      convert_tz = no
      sql = "{{TABLE}}.from"
    }
    to {
      description = Selected to range in carbon data
      type = time
      timeframes = [date, week, month, year]
      convert_tz = no
      sql = "{{TABLE}}.to"
    }
  }
}
