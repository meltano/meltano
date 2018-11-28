connection: "runners_db"

include: "*.view.ma"
label: "runners"

explore: {
  from: runners
  label: runners
  description: "GitLab CI Runners"
}
