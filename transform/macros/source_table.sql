{% macro quote(identifier) %}
  {{ return('"' ~ identifier ~ '"') }}
{% endmacro %}

{% macro source_table(table_name) %}
  {% set table_config = table_name ~ "_table" %}
  {{ return(quote(var("schema")) ~ "." ~ quote(var(table_config, table_name))) }}
{% endmacro %}
