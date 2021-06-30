<!---
1. Set the MR to delete the `release-next` branch when merged
2. The MR's title should be something similar to
   "Bump version: N.XX.zz -> N.YY.ww"
3. Don't set the MR to be automatically merged when the pipeline succeeds.
--->

- [ ] Wait for tag pipeline to succeed: https://gitlab.com/meltano/meltano/-/pipelines
  - [ ] Replace the pipeline link with a link to the publish job. Go to the commit's pipelines tab and select the one that has the publish stage.
  - _Successful completion includes publish to [PyPi](https://pypi.org/project/meltano/) and [DockerHub](https://hub.docker.com/r/meltano/meltano)_
- While waiting for the pipeline:
  - [ ] Post to https://meltano.com/blog/:
    - Copy content from previous release post and edit as appropriate. Be sure to credit community members for any contributions and link to their profile
  - [ ] Post to https://twitter.com/meltanodata/:
    - Typically: copy blog post introduction, add link to blog post, and edit down to fit inside character limit.
  - [ ] Slack:
    - [ ] Post to Meltano Slack `#announcements`
      - Copy blog post introduction, add `@channel` mention and link to blog post, change community member profile links to Slack member references if possible.
    - [ ] Post to Singer Slack `#meltano`
  - [ ] Make sure to check "delete the source branch" when the changes are merged.

/label ~Release ~"flow::Doing"
