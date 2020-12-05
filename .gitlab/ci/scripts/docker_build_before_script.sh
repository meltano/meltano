apk add git
export BASE_SHA=$(git hash-object poetry.lock)
echo Building Meltano on $BASE_SHA
