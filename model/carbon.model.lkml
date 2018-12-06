connection: "runners_db"

include: "region.view.lkml"
label: "carbon"

explore: region {
  from: region
  label: region
  description: "Region Carbon Region Data"

  join: entry {
    fields: [entry.from, entry.to]
    sql_on: ${region.id} = ${entry.region_id};;
    relationship: one_to_many
  }
}
