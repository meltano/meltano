{
  sql_table_name = gitlab.entry
  name = entry
  dimensions {
    id {
      label = ID
      primary_key = yes
      hidden = yes
      type = string
      sql = "{{table}}.id"
    }
    region_id {
      label = Region ID
      hidden = yes
      type = string
      sql = "{{table}}.id"
    }
  }
  dimension_groups {
    from {
      label = From
      description = Selected from range in carbon data
      type = time
      timeframes = [{ label = Date }, { label = Week }, { label = Month }, { label = Year }]
      convert_tz = no
      sql = "{{TABLE}}.from"
    }
    to {
      label = To
      description = Selected to range in carbon data
      type = time
      timeframes = [{ label = Date }, { label = Week }, { label = Month }, { label = Year }]
      convert_tz = no
      sql = "{{TABLE}}.to"
    }
  }
}
