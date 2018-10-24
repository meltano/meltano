{% macro source_table(table_name) %}
  {% set table_config = table_name ~ "_table" %}
  {{ return(var("schema") ~ "." ~ var(table_config, table_name)) }}
{% endmacro %}
