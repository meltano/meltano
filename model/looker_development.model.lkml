connection: "production_dw"

include: "*.view.lkml"         # include all views in this project

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
    view_label: "Users"
    type: inner
    relationship: one_to_one
    sql_on: ${f_opportunity.ownerid} = ${sfdc_user.id} ;;
  }

  join: sfdc_opportunity {
    view_label: "Dev Only - Raw SFDC Opportunity"
    type: full_outer
    relationship: one_to_one
    sql_on: ${f_opportunity.opportunity_id} = ${sfdc_opportunity.id} ;;
  }
}


explore: sao {
  from:  sfdc_sales_accepted_opportunity
  label: "Sales Accepted Opportunities"
  description: "List of SAOs"
}

explore: sfdc_opportunity {
  label: "Sales w/ Single Opp"
  view_label: "Opportunity"

  join: dim_opphistory {
    view_label: "Stage History"
#     type: inner
    relationship: one_to_one
    sql_on: ${sfdc_opportunity.id}=${dim_opphistory.opportunityid} ;;
  }

  join: sfdc_user {
    view_label: "Opportunity Owner"
    type: inner
    relationship: one_to_one
    sql_on: ${sfdc_opportunity.owner_id} = ${sfdc_user.id} ;;
  }

}
