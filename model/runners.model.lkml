connection: "runners_db"

include: "*.view.lkml"
label: "runners"

explore: {
  from: runners
  label: runners
  description: "GitLab CI Runners"
}
