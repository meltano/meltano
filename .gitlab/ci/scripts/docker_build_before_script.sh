apk add git
export BASE_SHA=$(git hash-object requirements.txt)
echo Building Meltano on $BASE_SHA