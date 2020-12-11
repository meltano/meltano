<!---
1. Set the MR to delete the `release-next` branch when merged
2. The MR's title should be something similar to
   "Bump version: N.XX.zz -> N.YY.ww"
3. Don't set the MR to be automatically merged when the pipeline succeeds.
--->
- [ ] Wait for tag pipeline to succeed: https://gitlab.com/meltano/meltano/-/pipelines
- [ ] Ensure https://pypi.org/project/meltano/ has been updated
- [ ] Post to https://meltano.com/blog/
- [ ] Post to https://twitter.com/meltanodata/
- [ ] Post to Meltano Slack `#announcements`
- [ ] Post to Singer Slack `#meltano`

/label ~Release ~"flow::Doing"
