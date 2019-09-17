<!---
1. Set the MR to delete the `release-next` branch when merged
2. The MR's title should be something similar to 
   "Bump version: N.XX.zz -> N.YY.ww"
3. Don't set the MR to be automatically merged when the pipeline succeeds.
   Wait for both the MR's pipeline and the tag pipeline to 
    successfully complete (green pipelines) and then manually merge the MR.
   Checking that the new version is available on pypi.org/project/meltano/
    is also a plus.
4. Add the url to the Release pipeline here:
--->
Release (Tag) pipeline:


/label ~Release