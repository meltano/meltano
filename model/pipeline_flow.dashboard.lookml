- dashboard: pipeline_analysis
  title: Pipeline Analysis
  layout: newspaper
  elements:
  - title: Pipeline Analysis
    name: Pipeline Analysis
    model: sales
    explore: pipeline_change
    type: looker_column
    fields:
    - pipeline_change.category
    - pipeline_change.acv_metric
    sorts:
    - pipeline_change.category
    limit: 500
    column_limit: 50
    dynamic_fields:
    - table_calculation: offset
      label: offset
      expression: if(${pipeline_change.category} = "Ending",0,running_total(offset(${starting},-1)+offset(${added},-1)-${subtracted}-${ending}))
      value_format:
      value_format_name: usd_0
      _kind_hint: measure
      _type_hint: number
    - table_calculation: starting
      label: Starting
      expression: if(${pipeline_change.category} = "Starting", ${pipeline_change.acv_metric},0)
      value_format:
      value_format_name: usd_0
      _kind_hint: measure
      _type_hint: number
    - table_calculation: added
      label: Added
      expression: "if(${pipeline_change.category} = \"Created\" OR ${pipeline_change.category}\
        \ = \"Moved In\" OR\n  ${pipeline_change.category} = \"Increased\" \n  , ${pipeline_change.acv_metric},0)"
      value_format:
      value_format_name: usd_0
      _kind_hint: measure
      _type_hint: number
    - table_calculation: subtracted
      label: Subtracted
      expression: |-
        if(${pipeline_change.category} = "Moved Out" OR ${pipeline_change.category} = "Decreased" OR
          ${pipeline_change.category} = "Won" OR
          ${pipeline_change.category} = "Lost"
          , -${pipeline_change.acv_metric},0)
      value_format:
      value_format_name: usd_0
      _kind_hint: measure
      _type_hint: number
    - table_calculation: ending
      label: Ending
      expression: if(${pipeline_change.category} = "Ending", ${pipeline_change.acv_metric},0)
      value_format:
      value_format_name: usd_0
      _kind_hint: measure
      _type_hint: number
    stacking: normal
    show_value_labels: true
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
    show_x_axis_label: false
    show_x_axis_ticks: true
    x_axis_scale: auto
    y_axis_scale_mode: linear
    ordering: none
    show_null_labels: false
    show_totals_labels: false
    show_silhouette: false
    totals_color: "#707070"
    show_row_numbers: true
    truncate_column_names: false
    hide_totals: false
    hide_row_totals: false
    table_theme: editable
    enable_conditional_formatting: false
    conditional_formatting_include_totals: false
    conditional_formatting_include_nulls: false
    series_types: {}
    hidden_fields:
    - pipeline_change.acv_metric
    series_colors:
      calculation_1: "#d4cceb"
      offset: transparent
      starting: "#00AAEA"
      added: "#0ABB45"
      subtracted: "#FC6250"
      ending: "#00AAEA"
    hidden_series: []
    label_color:
    - transparent
    - white
    - white
    - white
    - white
    hide_legend: true
    font_size: ''
    listen:
      Metric Type: pipeline_change.metric_type
      Date Range for Analysis: pipeline_change.date_range
      Opportunity Close Date: pipeline_change.close_date
    row: 0
    col: 0
    width: 24
    height: 9
  filters:
  - name: Metric Type
    title: Metric Type
    type: field_filter
    default_value: IACV
    model: sales
    explore: pipeline_change
    field: pipeline_change.metric_type
    listens_to_filters: []
    allow_multiple_values: true
    required: false
  - name: Date Range for Analysis
    title: Date Range for Analysis
    type: date_filter
    default_value: 30 days ago for 30 days
    allow_multiple_values: true
    required: false
  - name: Opportunity Close Date
    title: Opportunity Close Date
    type: date_filter
    default_value: this quarter
    allow_multiple_values: true
    required: false
