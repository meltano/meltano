connection: "production_dw"

include: "usage_*.view.lkml"
label: "product"

explore: usage_data {
  label: "Usage Data"
  description: "All dimensions are counts of that feature for a given instance."
}

explore: usage_data_month {
  label: "Monthly Max Usage Data"
}
