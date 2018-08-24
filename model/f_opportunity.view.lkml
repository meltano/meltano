view: f_opportunity {
  sql_table_name: analytics.f_opportunity ;;

  dimension: account_id {
    description: "This is the foreign key to dim_account"
    hidden: yes
    type: number
    sql: ${TABLE}.account_id ;;
  }

  dimension: acv {
    hidden: yes
    type: number
    sql: ${TABLE}.acv ;;
  }

  dimension: ownerid {
    hidden: yes
    type: string
    sql:${TABLE}.ownerid ;;
  }

  dimension: days_in_stage {
    type: number
    sql: ${TABLE}.days_in_stage ;;
  }

  dimension: deal_size {
    type: string
    sql: ${TABLE}.deal_size ;;
    drill_fields: [opportunity_name]
  }

  dimension: is_won {
    type: yesno
    sql: ${TABLE}.is_won ;;
  }

  dimension: reason_for_loss {
    type: string
    sql: ${TABLE}.reason_for_loss ;;
  }

  dimension: reason_for_loss_details {
    type: string
    sql: ${TABLE}.reason_for_loss_details ;;
  }

  dimension: risk_level {
    label: "Is Risky"
    type: yesno
    sql: ${TABLE}.is_risky ;;
  }

  dimension: last_activity{
    label: "Last Activity Date"
    type: date
    sql: ${TABLE}.lastactivitydate ;;
  }

  dimension: last_activity_days {
    label: "Last Activity - Days Since"
    type: number
    sql: date_part('day', now() - ${last_activity}) ;;
  }

  dimension: billing_period {
    type: string
    sql: ${TABLE}.billing_period ;;
  }

  dimension: competitor_unpacked {
    label: "Competitors - Unpacked"
    description: "Warning! This will cause double counting of opportunities and values because the opportunity is copied for each competitor listed!"
    type: string
    sql: unnest(string_to_array(${TABLE}.competitors__c, ';')) ;;
    # drill_fields: [detail*]
    link: {
      label: "Explore from here"
      url: "https://gitlab.looker.com/explore/sales/f_opportunity?f[f_opportunity.closedate_date]={{ _filters['f_opportunity.closedate_date'] | url_encode }}&f[dim_opportunitystage.mapped_stage]={{ _filters['dim_opportunitystage.mapped_stage'] | url_encode }}&f[dim_opportunitystage.isclosed]={{ _filters['dim_opportunitystage.isclosed'] | url_encode }}&f[f_opportunity.competitors]=%25{{ value }}%25&fields=f_opportunity.opportunity_name,f_opportunity.opportunity_type,dim_opportunitystage.mapped_stage,f_opportunity.total_iacv"
    }
  }

  dimension: competitors {
    label: "Competitors List"
    type: string
    sql: ${TABLE}.competitors__c ;;
  }

  dimension: iacv {
    type: number
    hidden: yes
    sql: ${TABLE}.iacv ;;
  }

  dimension: lead_source_id {
    hidden: yes
    type: number
    sql: ${TABLE}.lead_source_id ;;
  }

  dimension_group: closedate {
    label: "Close"
    type: time
    timeframes: [
      raw,
      date,
      week,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.opportunity_closedate ;;
  }

  dimension_group: created_date {
    label: "Created"
    type: time
    timeframes: [
      raw,
      date,
      week,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.opportunity_created_date ;;
  }

  dimension: opportunity_id {
    label: "ID"
    description: "The 18 char SFDC Opportunity ID"
    type: string
    sql: ${TABLE}.opportunity_id ;;
  }

  dimension: opportunity_name {
    label: "Name"
    description: "The name of the opportunity record from Salesforce."
    type: string
    sql: ${TABLE}.opportunity_name ;;

    link: {
      label: "Salesforce Opportunity"
      url: "https://na34.salesforce.com/{{ f_opportunity.opportunity_id._value }}"
      icon_url: "https://c1.sfdcstatic.com/etc/designs/sfdc-www/en_us/favicon.ico"
    }

  }

  dimension: opportunity_product {
    label: "Product Name"
    type: string
    sql: ${TABLE}.opportunity_product ;;
  }

  dimension: opportunity_sales_segmentation {
    label: "Sales Segmentation"
    type: string
    sql: ${TABLE}.opportunity_sales_segmentation ;;
  }

  dimension: opportunity_stage_id {
    description: "The foreign key to dim_opportunitystage"
    hidden: yes
    type: number
    sql: ${TABLE}.opportunity_stage_id ;;
  }

  dimension: opportunity_type {
    label: "Type"
    description: "The SFDC opportunity type (New, Renewal,Add-On Business)"
    type: string
    sql: ${TABLE}.opportunity_type ;;
  }

  dimension: quantity {
    label: "Product Quantity"
    type: number
    sql: ${TABLE}.quantity ;;
  }

  dimension: renewal_acv {
    hidden: yes
    type: number
    sql: ${TABLE}.renewal_acv ;;
  }

  dimension_group: sales_accepted {
    label: "Sales Accepted"
    type: time
    timeframes: [
      raw,
      date,
      week,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.sales_accepted_date ;;
  }

  dimension_group: sales_qualified {
    label: "Sales Qualified"
    type: time
    timeframes: [
      raw,
      date,
      week,
      month,
      quarter,
      year
    ]
    convert_tz: no
    datatype: date
    sql: ${TABLE}.sales_qualified_date ;;
  }

  dimension: sales_qualified_source {
    description: "Sales Qualified Source"
    type: string
    sql: ${TABLE}.sales_qualified_source ;;
  }

  dimension: tcv {
    label: "Total Contract Value"
    hidden: yes
    type: number
    sql: ${TABLE}.tcv ;;
  }

  dimension: upside_iacv {
    label: "Upside IACV"
    hidden: yes
    type:  number
    sql: ${TABLE}.upside_iacv ;;
  }

  dimension: upside_swing_deal_IACV {
    label: "Upside Swing Deal IACV"
    hidden:  yes
    type:  number
    sql: ${TABLE}.upside_swing_deal_iacv ;;
  }

  measure: number_of_opportunities {
    label: "Count of Opportunities"
    type: count_distinct
    sql: ${opportunity_id} ;;
    drill_fields: [detail*]
  }

  measure: total_tcv {
    label: "Contract Value (TCV)"
    type: sum
    sql: ${tcv} ;;
    drill_fields: [detail*]
    value_format_name: usd
  }

  measure: total_acv {
    label: "Annual Contract Value (ACV)"
    type: sum
    sql: ${acv} ;;
    drill_fields: [detail*]
    value_format_name: usd
    }

  measure: total_iacv {
    label: "Incremental Annual Contract Value (IACV)"
    type: sum
    sql: ${iacv} ;;
    drill_fields: [detail*]
    value_format_name: usd
    }

  measure: weighted_iacv {
    label: "Weighted IACV"
    type: sum
    sql:${iacv}* (${dim_opportunitystage.defaultprobability}/100) ;;
  }

  measure: upside_iacv_sum {
    label: "Upside IACV"
    type:  sum
    sql: ${upside_iacv} ;;
  }

  measure: upside_swing_deal_IACV_sum {
    label: "Upside Swing Deal IACV"
    type:  sum
    sql: ${upside_swing_deal_IACV} ;;
  }

  measure: total_sqos {
    label: "Total Sales Qualified Opportunities (SQOs)"
    type: count_distinct
    sql:  ${opportunity_id} ;;
    filters: {
      field: dim_leadsource.initial_source
      value: "-Web Direct"
    }
    filters: {
      field: iacv
      value: ">=0"
    }
    filters: {
      field: sales_qualified_date
      value: "-NULL"
    }
    drill_fields: [detail*]
  }

  measure: total_saos {
    label: "Total Sales Accepted Opportunities (SAOs)"
    type: count_distinct
    sql:  ${opportunity_id} ;;
    filters: {
      field: dim_leadsource.initial_source
      value: "-Web Direct"
    }
    filters: {
      field: iacv
      value: ">=0"
    }
    filters: {
      field: sales_accepted_date
      value: "-NULL"
    }
    drill_fields: [detail*]
  }

  measure: total_sao_iacv {
    label: "Total Sales Accepted Opportunity (SAO) IACV"
    type: sum
    sql:  ${iacv} ;;
    filters: {
      field: dim_leadsource.initial_source
      value: "-Web Direct"
    }
    filters: {
      field: iacv
      value: ">=0"
    }
    filters: {
      field: sales_accepted_date
      value: "-NULL"
    }
    drill_fields: [detail*]
  }

  measure: total_sqo_iacv {
    label: "Total Sales Qualified Opportunity (SQO) IACV "
    type: sum
    sql:   ${iacv} ;;
    filters: {
      field: dim_leadsource.initial_source
      value: "-Web Direct"
    }
    filters: {
      field: iacv
      value: ">=0"
    }
    filters: {
      field: sales_qualified_date
      value: "-NULL"
    }
    drill_fields: [detail*]
  }

  measure: opp_renewal_acv {
    label: "Renewal ACV"
    type: sum
    sql: ${TABLE}.renewal_acv ;;
    drill_fields: [detail*]
    value_format_name: usd
  }

  measure: total_quantity {
    label: "Total Quantity"
    type: sum
    sql: ${quantity} ;;
    drill_fields: [detail*]
  }

  set: detail {
    fields: [
      dim_account.name, opportunity_name, opportunity_sales_segmentation, opportunity_type, closedate_date, total_iacv, total_acv
    ]
  }
}
