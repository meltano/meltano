apk add git
export BASE_SHA=$(git hash-object poetry.lock)
echo Building Meltano on $BASE_SHA
export PYTHON_IMAGE_VERSION=$(echo $PYTHON_VERSION | cut -d "." -f1-2)
echo python_image_version set to $PYTHON_IMAGE_VERSION
