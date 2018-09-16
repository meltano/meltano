{#
-- Netsuite Docs: http://www.netsuite.com/help/helpcenter/en_US/srbrowser/Browser2016_1/schema/record/department.html
#}

with base as (

    SELECT *
    FROM netsuite.departments

), renamed as (

        SELECT internal_id as department_id,
               name as department_name,
               include_children as does_include_children,
               is_inactive,
               parent_id as parent_department_id,
               parent_name as parent_deparment_name
              --subsidiary_list -- IS JSON
              --custom_field_list -- IS JSON
    FROM base
)

SELECT *
FROM renamed
