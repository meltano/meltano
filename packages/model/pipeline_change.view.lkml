view: pipeline_change {
  derived_table: {
    sql: WITH NEW AS
        (SELECT *
         FROM analytics.f_snapshot_opportunity a
         INNER JOIN dim_opportunitystage s ON a.opportunity_stage_id=s.stage_id
         WHERE
              date(snapshot_date) = {% date_end date_range %}
          AND s.mapped_stage != 'Unmapped'
          ),

         OLD AS
        (SELECT *
         FROM analytics.f_snapshot_opportunity a
         INNER JOIN dim_opportunitystage os ON a.opportunity_stage_id=os.stage_id
         WHERE
              date(snapshot_date) = {% date_start date_range %}
          AND os.mapped_stage != 'Unmapped'
          )

      SELECT
        'Starting' AS category,
        '1' AS order,
        NULL::date as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        OLD.*
      FROM OLD
      WHERE (OLD.sales_accepted_date < {% date_start date_range %}
            OR old.sales_accepted_date ISNULL
            OR old.opportunity_closedate= {% date_start date_range %})
        AND {% condition close_date %} opportunity_closedate {% endcondition %}
        AND old.is_closed=FALSE
        AND old.mapped_stage != '0-Pending Acceptance'

      UNION ALL

      SELECT
        'Created' as category ,
        '2' as order,
        NULL::date as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        NEW.*
      FROM NEW
      WHERE NEW.sales_accepted_date >= {% date_start date_range %}
        AND NEW.sales_accepted_date <= {% date_end date_range %}
        AND {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND (
              NEW.is_closed=false
              OR
              (NEW.is_closed=true AND NEW.is_won = true)
            )

      UNION ALL
  -- For opps that show up w/o a sales_accepted_date and aren't in the OLD list
      SELECT
        'Created' As category ,
        '2' AS order,
        NULL::date as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        NEW.*
      FROM NEW
      FULL JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND NEW.sales_accepted_date ISNULL
        AND NEW.opportunity_closedate >= {% date_start date_range %}
        AND
            (
              (OLD.opportunity_name ISNULL AND (OLD.mapped_stage != '0-Pending Acceptance' OR OLD.mapped_stage ISNULL) AND NEW.is_closed=false AND NEW.mapped_stage != '0-Pending Acceptance')
              OR
              (OLD.mapped_stage = '0-Pending Acceptance' AND NEW.is_closed=true)
              OR
              (OLD.mapped_stage = '0-Pending Acceptance' AND NEW.mapped_stage
                  IN ('1-Discovery','2-Scoping','3-Technical Evaluation','4-Propoasl','5-Negotiating','6-Awaiting Signature'))
              OR
              (OLD.opportunity_name ISNULL and NEW.is_closed=true AND NEW.is_won=true)
              OR
              (NEW.opportunity_closedate = {% date_start date_range %} and NEW.is_closed=true AND NEW.is_won=true)
            )

      UNION ALL

      SELECT
        'Moved In' AS category,
        '3' AS order,
        OLD.opportunity_closedate as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        NEW.*
      FROM NEW
      FULL JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE ( OLD.opportunity_closedate < {% date_start close_date %}
        OR OLD.opportunity_closedate >= {% date_end close_date %} )
        AND {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND OLD.mapped_stage != '0-Pending Acceptance'

      UNION ALL

      SELECT
        'Increased' AS category,
        '4' AS order,
        NULL::date as previous_close_date,
        OLD.iacv as previous_iacv,
        OLD.acv as previous_acv,
        OLD.tcv as previous_tcv,
        OLD.renewal_acv as previous_renewal_acv,
        NEW.*
      FROM NEW
      FULL JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE ( OLD.opportunity_closedate >= {% date_start close_date %}
        AND OLD.opportunity_closedate < {% date_end close_date %})
        AND {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND NEW.iacv > old.iacv
        AND OLD.is_closed=false
        AND OLD.mapped_stage != '0-Pending Acceptance'

      UNION ALL

      SELECT
        'Decreased' AS category,
        '6' AS order,
        NULL::date as previous_close_date,
        OLD.iacv as previous_iacv,
        OLD.acv as previous_acv,
        OLD.tcv as previous_tcv,
        OLD.renewal_acv as previous_renewal_acv,
        NEW.*
      FROM NEW
      FULL JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE ( OLD.opportunity_closedate >= {% date_start close_date %}
        AND OLD.opportunity_closedate < {% date_end close_date %})
        AND {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND NEW.iacv < OLD.iacv
        AND OLD.is_closed=false
        AND OLD.mapped_stage != '0-Pending Acceptance'

      UNION ALL

      SELECT
        'Moved Out' AS category,
        '5' AS order,
        OLD.opportunity_closedate as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        NEW.*
      FROM NEW
      FULL JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE ( NEW.opportunity_closedate < {% date_start close_date %}
        OR NEW.opportunity_closedate >= {% date_end close_date %})
        AND {% condition close_date %} OLD.opportunity_closedate {% endcondition %}
        AND OLD.is_closed=false
        AND OLD.mapped_stage != '0-Pending Acceptance'

      UNION ALL

      SELECT
          'Won' AS category,
          '7' AS order,
          NULL::date as previous_close_date,
          0.0::float as previous_iacv,
          0.0::float as previous_acv,
          0.0::float as previous_tcv,
          0.0::float as previous_renewal_acv,
          NEW.*
      FROM NEW
      FULL JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND NEW.is_won=true
        AND (OLD.is_closed=false OR NEW.opportunity_closedate = {% date_start date_range %})
        AND NEW.opportunity_closedate >= {% date_start date_range %}

      UNION ALL
        -- This is for opps that are won but don't show up in the old list
      SELECT
        'Won' AS category,
        '7' AS order,
        NULL::date as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        NEW.*
      FROM NEW
      FULL JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND NEW.is_won = true
        AND OLD.opportunity_name ISNULL
        AND NEW.opportunity_closedate >= {% date_start date_range %}

      UNION ALL

      SELECT
        'Lost' AS category,
        '8' AS order,
        NULL::date as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        NEW.*
      FROM NEW
      INNER JOIN OLD ON OLD.opportunity_id=NEW.opportunity_id
      WHERE {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND NEW.is_won=false
        AND NEW.is_closed=true
        AND OLD.is_closed=false
        AND OLD.stage_id != '33' --duplicates
        AND NEW.reason_for_loss != 'Merged into another opportunity'

      UNION ALL

       SELECT
        'Ending' as category,
        '9' as order,
        NULL::date as previous_close_date,
        0.0::float as previous_iacv,
        0.0::float as previous_acv,
        0.0::float as previous_tcv,
        0.0::float as previous_renewal_acv,
        NEW.*
      FROM NEW
      WHERE {% condition close_date %} NEW.opportunity_closedate {% endcondition %}
        AND NEW.is_closed=FALSE
        ANd NEW.mapped_stage != '0-Pending Acceptance'
       ;;
  }

  filter: date_range {
    convert_tz: no
    type: date
  }

  filter: close_date {
    convert_tz: no
    type: date
  }


  dimension: category {
    type: string
    sql: ${TABLE}.category ;;
    order_by_field: order
    suggestions: ["Starting", "Created","Moved In", "Increased","Decreased","Moved Out","Won","Lost"]
    link: {
      label: "Explore from here"
      url: "https://gitlab.looker.com/explore/sales/pipeline_change?f[pipeline_change.category]={{ pipeline_change.category }}&f[pipeline_change.close_date]={{ _filters['pipeline_change.close_date'] | url_encode }}&f[pipeline_change.date_range]={{ _filters['pipeline_change.date_range'] | url_encode }}&f[pipeline_change.metric_type]={{ _filters['pipeline_change.metric_type'] | url_encode }}&fields=pipeline_change.opportunity_name,pipeline_change.opportunity_type,dim_opportunitystage.mapped_stage,pipeline_change.total_iacv"
    }
  }

  dimension: order {
    type: number
    sql: ${TABLE}.order ;;
  }

  dimension: opportunity_id {
#     hidden: yes
    type: string
    sql: ${TABLE}.opportunity_id ;;
  }

  dimension_group: snapshot {
    type: time
    timeframes: [raw, date]
    sql: ${TABLE}.snapshot_date ;;
  }

  dimension: account_id {
    hidden: yes
    type: number
    sql: ${TABLE}.account_id ;;
  }

  dimension: opportunity_stage_id {
    hidden: yes
    type: number
    sql: ${TABLE}.opportunity_stage_id ;;
  }

  dimension: lead_source_id {
    hidden: yes
    type: number
    sql: ${TABLE}.lead_source_id ;;
  }

  dimension: reason_for_loss {
    type: string
    sql: ${TABLE}.reason_for_loss ;;
  }

  dimension: reason_for_loss_details {
    label: "Reason for Loss - Details"
    type: string
    sql: ${TABLE}.reason_for_loss_details ;;
  }

  dimension: opportunity_type {
    label: "Type"
    type: string
    sql: ${TABLE}.opportunity_type ;;
  }

  dimension: opportunity_sales_segmentation {
    label: "Sales Segmentation"
    type: string
    sql: ${TABLE}.opportunity_sales_segmentation ;;
  }

  dimension: ownerid {
    hidden: yes
    type: string
    sql: ${TABLE}.ownerid ;;
  }

  dimension_group: sales_qualified {
    type: time
    timeframes: [raw, date]
    sql: ${TABLE}.sales_qualified_date ;;
  }

  dimension_group: sales_accepted {
    type: time
    timeframes: [raw, date]
    sql: ${TABLE}.sales_accepted_date ;;
  }

  dimension: sales_qualified_source {
    type: string
    sql: ${TABLE}.sales_qualified_source ;;
  }

  dimension_group: opportunity_close {
    label: "Close"
    type: time
    timeframes: [raw, date]
    sql: ${TABLE}.opportunity_closedate ;;
  }

  dimension_group: prev_opportunity_close {
    label: "Previous Close"
    type: time
    timeframes: [raw, date]
    sql: ${TABLE}.previous_close_date ;;
  }

  dimension: opportunity_name {
    label: "Name"
    type: string
    sql: ${TABLE}.opportunity_name ;;

    link: {
      label: "Salesforce Opportunity"
      url: "https://na34.salesforce.com/{{ pipeline_change.opportunity_id._value }}"
      icon_url: "https://c1.sfdcstatic.com/etc/designs/sfdc-www/en_us/favicon.ico"
    }
  }

  dimension: iacv {
    label: "IACV"
    hidden: yes
    type: number
    sql: ${TABLE}.iacv ;;
  }

  dimension: renewal_acv {
    label: "Renewal ACV"
    hidden: yes
    type: number
    sql: ${TABLE}.renewal_acv ;;
  }

  dimension: acv {
    hidden: yes
    type: number
    sql: ${TABLE}.acv ;;
  }

  dimension: tcv {
    hidden: yes
    type: number
    sql: ${TABLE}.tcv ;;
  }

  measure: sum_iacv {
    group_label: "Current Values"
    label: "Current IACV"
    type: sum
    sql: ${TABLE}.iacv ;;
  }

  measure: sum_renewal_acv {
    group_label: "Current Values"
    label: "Current Renewal ACV"
    type: sum
    sql: ${TABLE}.renewal_acv ;;
  }

  measure: sum_acv {
    group_label: "Current Values"
    label: "Current ACV"
    type: sum
    sql: ${TABLE}.acv ;;
  }

  measure: sum_tcv {
    group_label: "Current Values"
    label: "Current TCV"
    type: sum
    sql: ${TABLE}.tcv ;;
  }


  parameter: metric_type {
    description: "Choose which ACV type to measure"
    allowed_value: { value: "ACV" }
    allowed_value: { value: "IACV" }
    allowed_value: { value: "Renewal ACV" }
    allowed_value: { value: "TCV" }
    default_value: "IACV"
  }

  measure: acv_metric {
    label: "ACV Metric"
    description: "use the metric type filter to choose which ACV to measure"
    type: number
    sql: CASE
          WHEN {% parameter metric_type %} = 'ACV' THEN ${total_acv}
          WHEN {% parameter metric_type %} = 'IACV' THEN ${total_iacv}
          WHEN {% parameter metric_type %} = 'Renewal ACV' THEN ${total_renewal_acv}
          WHEN {% parameter metric_type %} = 'TCV' THEN ${total_tcv}
        END ;;
    label_from_parameter: metric_type
    value_format_name: usd
    drill_fields: [detail*]
  }

  dimension: prev_iacv {
    label: "Previous IACV"
    hidden: yes
    type: number
    sql: ${TABLE}.previous_iacv ;;
  }

  dimension: prev_tcv {
    label: "Previous TCV"
    hidden: yes
    type: number
    sql: ${TABLE}.previous_tcv ;;
  }

  dimension: prev_acv {
    label: "Previous ACV"
    hidden: yes
    type: number
    sql: ${TABLE}.previous_acv ;;
  }

  dimension: prev_renewal {
    label: "Previous Renewal ACV"
    hidden: yes
    type: number
    sql: ${TABLE}.previous_renewal_acv ;;
  }

  measure: sum_prev_iacv {
    group_label: "Previous Values"
    label: "Previous IACV"
    type: sum
    sql: ${TABLE}.previous_iacv ;;
  }

  measure: sum_prev_tcv {
    group_label: "Previous Values"
    label: "Previous TCV"
    type: sum
    sql: ${TABLE}.previous_tcv ;;
  }

  measure: sum_prev_acv {
    group_label: "Previous Values"
    label: "Previous ACV"
    type: sum
    sql: ${TABLE}.previous_acv ;;
  }

  measure: sum_prev_renewal {
    group_label: "Previous Values"
    label: "Previous Renewal ACV"
    type: sum
    sql: ${TABLE}.previous_renewal_acv ;;
  }

  measure: total_acv {
    hidden: yes
    label: "ACV Change"
    type: sum
    sql: CASE
          WHEN ${category} IN ('Starting', 'Created', 'Moved In', 'Ending') THEN ${acv}
          WHEN ${category} IN ('Increased','Decreased') THEN ${acv} - ${prev_acv}
          WHEN ${category} IN ('Moved Out', 'Won', 'Lost') THEN -1.0*${acv}
        END ;;
    value_format_name: usd
  }

  measure: total_iacv {
    hidden: yes
    label: "IACV Change"
    type: sum
    sql: CASE
          WHEN ${category} IN ('Starting', 'Created', 'Moved In', 'Ending') THEN ${iacv} - ${prev_iacv}
          WHEN ${category} IN ('Increased','Decreased') THEN ${iacv} - ${prev_iacv}
          WHEN ${category} IN ('Moved Out', 'Won', 'Lost') THEN -1.0*${iacv} - ${prev_iacv}
        END ;;
    value_format_name: usd
  }

  measure: total_renewal_acv {
    hidden: yes
    label: "Renewal ACV Change"
    type: sum
    sql: CASE
          WHEN ${category} IN ('Starting', 'Created', 'Moved In', 'Ending') THEN ${renewal_acv}
          WHEN ${category} IN ('Increased','Decreased') THEN ${renewal_acv} - ${prev_renewal}
          WHEN ${category} IN ('Moved Out', 'Won', 'Lost') THEN -1.0*${renewal_acv}
        END ;;
    value_format_name: usd
  }

  measure: total_tcv {
    hidden: yes
    label: "TCV Change"
    type: sum
    sql: CASE
          WHEN ${category} IN ('Starting', 'Created', 'Moved In', 'Ending') THEN ${tcv}
          WHEN ${category} IN ('Increased','Decreased') THEN ${tcv} - ${prev_tcv}
          WHEN ${category} IN ('Moved Out', 'Won', 'Lost') THEN -1.0*${tcv}
        END ;;
    value_format_name: usd
  }

  measure: count {
    type: count
  }

  set: detail {
    fields: [
    ]
  }
}
