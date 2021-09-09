# when extending .parallel:python_version this will set $PYTHON_IMAGE_VERSION to a version string only consisting
# of the major.minor version, stripping of any other version levels. i.e. 3.9.6 -> 3.9. This allows for building
# with specific python version's but still creating "generic" major.minor based images.
export PYTHON_IMAGE_VERSION=$(echo $PYTHON_VERSION | cut -d "." -f1-2)
echo python_image_version set to $PYTHON_IMAGE_VERSION
