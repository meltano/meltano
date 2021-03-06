<!---
1. Set the MR to delete the `release-next` branch when merged
2. The MR's title should be something similar to
   "Bump version: N.XX.zz -> N.YY.ww"
3. Don't set the MR to be automatically merged when the pipeline succeeds.
--->

- [ ] Wait for tag pipeline to succeed: https://gitlab.com/meltano/meltano/-/pipelines
- [ ] Ensure https://pypi.org/project/meltano/ has been updated
- [ ] Ensure https://hub.docker.com/r/meltano/meltano has been updated
- [ ] Post to https://meltano.com/blog/:
  - Copy content from previous release post and edit as appropriate. Be sure to credit community members for any contributions and link to their profile
- [ ] Post to https://twitter.com/meltanodata/:
  - Typically: copy blog post introduction, add link to blog post, and edit down to fit inside character limit.
- [ ] Post to Meltano Slack `#announcements` and share in `#general`
  - Copy blog post introduction, add `@channel` mention and link to blog post, change community member profile links to Slack member references if possible.
- [ ] Post to Singer Slack `#meltano`

/label ~Release ~"flow::Doing"
