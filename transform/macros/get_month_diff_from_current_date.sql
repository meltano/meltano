
{% macro get_month_diff_from_current_date(month_diff) %}



    {% if  month_diff == 0 %}

        {%- call statement('get_now', fetch_result=True) %}

            select current_date

        {%- endcall -%}


        {%- set value_list = load_result('get_now') -%}

        {%- if value_list and value_list['data'] -%}

            {%- set loop_date = value_list['data'] | map(attribute=0) | list %}

            {{ return(loop_date[0]) }}

        {%- else -%}

            {{ return(1) }}

        {%- endif -%}



    {% else %}

        {%- call statement('get_month_diff', fetch_result=True) %}

            select date_trunc('month', current_date) - '{{ month_diff }} month'::INTERVAL + '1 month'::INTERVAL - '1 day'::INTERVAL

        {%- endcall -%}


        {%- set value_list = load_result('get_month_diff') -%}

        {%- if value_list and value_list['data'] -%}

            {%- set loop_date = value_list['data'] | map(attribute=0) | list %}

            {{ return(loop_date[0]) }}

        {%- else -%}

            {{ return(1) }}

        {%- endif -%}

    {%- endif -%}



{% endmacro %}