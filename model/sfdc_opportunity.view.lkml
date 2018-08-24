view: sfdc_opportunity {
  sql_table_name: analytics.sfdc_opportunity_xf;;
  # # Define your dimensions and measures here, like this:
  dimension: id {
    primary_key: yes
    hidden: yes
    type: string
    sql: ${TABLE}.opportunity_id ;;
  }

  dimension: owner_id {
    hidden: yes
    type: string
    sql: ${TABLE}.owner_id ;;
  }

  dimension: stage_id {
    hidden: yes
    type: string
    sql: ${TABLE}.opportunity_stage_id ;;
  }

  #
#   dimension: isdeleted {
#     label: "Is Deleted"
#     description: "Filter out corrupt data"
#     type: yesno
#     sql: ${TABLE}.is_deleted ;;
#   }
  #
  dimension: subscription_type {
    description: "Sale type based on subscription"
    type: string
    sql: ${TABLE}.sales_type ;;
  }

  dimension: opportunity_name {
    type: string
    sql: ${TABLE}.opportunity_name ;;

    link: {
      label: "Salesforce Opportunity"
      url: "https://na34.salesforce.com/{{ sfdc_opportunity.id._value }}"
      icon_url: "https://c1.sfdcstatic.com/etc/designs/sfdc-www/en_us/favicon.ico"
    }
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
  #
  dimension: sale_stage {
    description: "Stage in which a sale is in"
    type: string
    sql: ${TABLE}.stage_name ;;
  }
  #
  dimension_group: closedate {
    description: "The date when an opportunity was closed"
    label: "Close"
    type: time
    convert_tz: no
    timeframes: [date, week, month, year]
    sql: ${TABLE}.close_date ;;
  }

  dimension_group: createddate {
    description: "The date when an opportunity was created"
    label: "Created"
    type: time
    convert_tz: no
    timeframes: [date, week, month, year]
    sql: ${TABLE}.created_date ;;
  }
  #
  dimension: sale_type {
    description: "Sales assisted or web direct sale"
    type: string
    sql: ${TABLE}.sales_type ;;
  }
  #
  dimension: products {
    description: "Product that is tied to opportunity"
    type: string
    sql: ${TABLE}.products_purchased ;;
  }

  measure: tcv {
    label: "TCV - Total Contract Value"
    type: sum
    sql: ${TABLE}.total_contract_value ;;
    value_format: "$#,##0"
  }
#
  measure: renewal_amt {
    description: "Renewal Amount"
    type: sum
    sql: ${TABLE}.renewal_amount ;;
    value_format: "$#,##0"
  }
#
  measure: renewal_acv {
    label: "Renewal ACV"
    type: sum
    sql: ${TABLE}.renewal_acv ;;
    value_format: "$#,##0"
  }
#
  measure: acv {
    label: "ACV - Annual contract value"
    type: sum
    sql: ${TABLE}.acv ;;
    value_format: "$#,##0"
  }
#
  measure: iacv {
    label: "IACV - Incremental annual contract value"
    type: sum
    sql: ${TABLE}.incremental_acv ;;
    value_format: "$#,##0"
  }
#
  measure: nrv {
    label: "NRV - Non Recurring Value"
    description: "Example: proserv, training, etc."
    type: sum
    sql: ${TABLE}.nrv ;;
    value_format: "$#,##0"
  }

  measure: upside_iacv {
    label: "Upside IACV"
    type:  sum
    sql: ${TABLE}.upside_iacv ;;
  }

  measure: upside_swing_deal_IACV {
    label: "Upside Swing Deal IACV"
    type:  sum
    sql: ${TABLE}.upside_swing_deal_iacv ;;
  }

}
