connection: "production_dw"

include: "*.view.lkml"         # include all views in this project
#include: "*.dashboard.lookml"  # include all dashboards in this project
label: "finance"

explore: bookings {
  from: sfdc_opportunity
  label: "Bookings"
  description: "Bookings Metrics (ex: TCV, IACV)"
  always_filter: {
    filters: {
      field: sale_stage
      value: "Closed Won"
    }
    filters: {
      field: subscription_type
      value: "-Reseller"
    }
  }

}
#
explore: invoicing {
  view_label: "Invoicing"
  from:  zuora_ar
  label: "A/R Aging"
  description: "A/R Oustanding"

  join: zuora_invoices_beyond_30days {
  fields: []
  view_label: "Invoicing"
  sql_on:     ${invoicing.customer} = ${zuora_invoices_beyond_30days.account_name}
          AND ${invoicing.day_range} = ${zuora_invoices_beyond_30days.day_range};;
  relationship: many_to_one
  }
}

explore: customers_and_arr {
  from: zuora_current_arr
  label: "Current ARR & Customers"
}

explore: pipeline {
  from: sfdc_pipeline
  label: "Sales Pipeline"
  description: "Pipeline Opportunities"
}

explore: closed_deals {
  from: sfdc_closed_deals_acv
  label: "Closed Deals"
  description: "Closed Deals & ACV/New Customer"
}

explore: total_employees {
  from: historical_headcount
  label: "Total Employees"
  description: "Total Employees"
}

explore: corp_metrics {
  from: historical_metrics
  label: "Corporate Metrics"
  description: "Corporate Metrics"
}
