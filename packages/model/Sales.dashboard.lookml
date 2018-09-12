- dashboard: sales
  title: Sales
  layout: newspaper
  elements:
  - title: IACV by Segment by Month
    name: IACV by Segment by Month
    model: sales
    explore: f_opportunity
    type: looker_column
    fields:
    - f_opportunity.total_iacv
    - dim_account.sales_segmentation
    - f_opportunity.closedate_month
    pivots:
    - dim_account.sales_segmentation
    fill_fields:
    - f_opportunity.closedate_month
    filters:
      f_opportunity.closedate_month: 8 quarters
      dim_opportunitystage.iswon: 'Yes'
    sorts:
    - dim_account.sales_segmentation 0
    - f_opportunity.closedate_month desc
    limit: 500
    column_limit: 50
    stacking: normal
    show_value_labels: false
    label_density: 25
    legend_position: center
    x_axis_gridlines: false
    y_axis_gridlines: true
    show_view_names: false
    limit_displayed_rows: false
    y_axis_combined: true
    show_y_axis_labels: true
    show_y_axis_ticks: true
    y_axis_tick_density: default
    y_axis_tick_density_custom: 5
    show_x_axis_label: true
    show_x_axis_ticks: true
    x_axis_scale: time
    y_axis_scale_mode: linear
    ordering: none
    show_null_labels: false
    show_totals_labels: true
    show_silhouette: false
    totals_color: "#000000"
    hidden_series: []
    x_axis_datetime_label: "%b %y"
    label_value_format: $0.000,," M"
    listen:
      Is Large and Up?: dim_account.is_lau
    row: 0
    col: 0
    width: 24
    height: 16
  filters:
  - name: Close Date
    title: Close Date
    type: date_filter
    default_value: 8 quarters
    allow_multiple_values: true
    required: false
  - name: Is Large and Up?
    title: Is Large and Up?
    type: field_filter
    default_value: ''
    model: sales
    explore: f_opportunity
    field: dim_account.is_lau
    listens_to_filters: []
    allow_multiple_values: true
    required: false
