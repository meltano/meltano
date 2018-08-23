connection: "production_dw"

include: "*.view.lkml"         # include all views in this project
include: "*.dashboard.lookml"  # include all dashboards in this project



explore: f_opportunity {
  label: "Sales"
  description: "Start here for questions around Sales data"

  view_label: "Opportunity"

  join: dim_account {
    view_label: "Account"
    type: inner
    relationship: many_to_one
    sql_on: ${f_opportunity.account_id} = ${dim_account.id} ;;
  }

  join: dim_leadsource {
    view_label: "Lead Source"
    type: inner
    relationship: many_to_one
    sql_on: ${f_opportunity.lead_source_id} = ${dim_leadsource.id} ;;
  }

  join: dim_opportunitystage {
    view_label: "Opportunity Stage"
    type: inner
    relationship: many_to_one
    sql_on: ${f_opportunity.opportunity_stage_id} = ${dim_opportunitystage.id} ;;
  }

  join: sfdc_user {
    view_label: "Opportunity Owner"
    type: inner
    relationship: many_to_one
    sql_on: ${f_opportunity.ownerid} = ${sfdc_user.id} ;;
  }

  join: dim_date {
    view_label: "Close Date Info"
    type: full_outer
    relationship: one_to_one
    sql_on: ${f_opportunity.closedate_date}=${dim_date.date_actual_date} ;;
  }

  join: dim_opphistory {
    view_label: "Stage History"
    type: inner
    relationship: one_to_many
    sql_on: ${f_opportunity.opportunity_id}=${dim_opphistory.opportunityid} ;;
  }

  join: bookings_goal {
    relationship: many_to_one
    sql_on: ${f_opportunity.closedate_date}=${bookings_goal.goal_month} ;;
  }

  join: historical_sales_quota_xf {
    relationship: many_to_one
    sql_on: ${f_opportunity.ownerid} = ${historical_sales_quota_xf.account_owner_id}
        AND ${dim_date.date_actual_month} = ${historical_sales_quota_xf.quota_month_month};;
  }

  join: historical_sales_quota {
    relationship: many_to_one
    sql_on: UPPER(${historical_sales_quota.account_owner}) = UPPER(${historical_sales_quota_xf.account_owner_name}) ;;
  }

}

explore: sfdc_opportunity {
  label: "Sales w/ Single Opportunity View"
  view_label: "Opportunity"

  join: dim_opphistory {
    view_label: "Stage History"
    type: inner
    relationship: one_to_many
    sql_on: ${sfdc_opportunity.id}=${dim_opphistory.opportunityid} ;;
  }

  join: sfdc_user {
    view_label: "Opportunity Owner"
    type: inner
    relationship: many_to_one
    sql_on: ${sfdc_opportunity.owner_id} = ${sfdc_user.id} ;;
  }

  join: dim_opportunitystage {
    view_label: "Opportunity Stage"
    type: inner
    relationship: many_to_one
    sql_on: ${sfdc_opportunity.stage_id} = ${dim_opportunitystage.id} ;;
  }

}

explore: f_snapshot_opportunity {
  label: "Historical Opportunities"
  description: "Start here for questions around Sales data"

  view_label: "Opportunity"

  join: dim_account {
    view_label: "Account"
    type: inner
    relationship: many_to_one
    sql_on: ${f_snapshot_opportunity.account_id} = ${dim_account.id} ;;
  }

  join: dim_leadsource {
    view_label: "Lead Source"
    type: inner
    relationship: many_to_one
    sql_on: ${f_snapshot_opportunity.lead_source_id} = ${dim_leadsource.id} ;;
  }

  join: dim_opportunitystage {
    view_label: "Opportunity Stage"
    type: inner
    relationship: many_to_one
    sql_on: ${f_snapshot_opportunity.opportunity_stage_id} = ${dim_opportunitystage.id} ;;
  }

  join: sfdc_user {
    view_label: "Users"
    type: inner
    relationship: one_to_one
    sql_on: ${f_snapshot_opportunity.ownerid} = ${sfdc_user.id} ;;
  }

  join: dim_date {
    view_label: "Close Date Info"
    type: full_outer
    relationship: one_to_one
    sql_on: ${f_snapshot_opportunity.opportunity_closedate}=${dim_date.date_actual_date} ;;
  }
}

explore: pipeline_change {
  label: "Sales Pipeline Change"
  description: "Use this explore to look at the change in pipeline over time"

  conditionally_filter: {
    filters: {
      field: close_date
      value: "this month"
    }

    filters: {
      field: date_range
      value: "7 days ago for 7 days"
    }

    filters: {
      field: metric_type
      value: "IACV"
    }
  }

  join: dim_opportunitystage {
    view_label: "Opportunity Stage"
    type: inner
    relationship: one_to_one
    sql_on: ${pipeline_change.opportunity_stage_id} = ${dim_opportunitystage.id} ;;
  }

  join: sfdc_user {
    view_label: "Opportunity Owner"
    type: inner
    relationship: one_to_one
    sql_on: ${pipeline_change.ownerid} = ${sfdc_user.id} ;;
  }

  join: dim_leadsource {
    view_label: "Lead Source"
    type: inner
    relationship: many_to_one
    sql_on: ${pipeline_change.lead_source_id} = ${dim_leadsource.id} ;;
  }
}

explore: f_churn_history {
  label: "Parent Account Churn History"
  description: "Use this explore to look at parent subscription churn"

  join: dim_account {
    view_label: "Account"
    type: inner
    relationship: many_to_one
    sql_on: ${f_churn_history.id} = ${dim_account.sfdc_account_id} ;;
  }
}

explore: f_acct_churn_history {
  label: "Child Account Churn History"
  description: "Use this explore to look at child subscription churn"

  join: dim_account {
    view_label: "Account"
    type: inner
    relationship: many_to_one
    sql_on: ${f_acct_churn_history.id} = ${dim_account.sfdc_account_id} ;;
  }
}
