<!---
1. Set the MR to delete the `release-next` branch when merged
2. The MR's title should be something similar to
   "Bump version: N.XX.zz -> N.YY.ww"
3. Don't set the MR to be automatically merged when the pipeline succeeds.
--->

- [ ] Wait for tag pipeline to succeed: https://gitlab.com/meltano/meltano/-/pipelines
  - [ ] Replace the pipeline link with a link to the publish job. Go to the commit's pipelines tab and select the one that has the publish stage.
  - [ ] Check to confirm successful publish to [PyPi](https://pypi.org/project/meltano/) and [DockerHub](https://hub.docker.com/r/meltano/meltano)_

-----------------------------------

Ref: https://handbook.meltano.com/engineering/#release-process

/label ~Release ~"flow::Doing"
