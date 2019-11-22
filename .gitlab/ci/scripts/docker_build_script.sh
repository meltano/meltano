docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
docker build -t $IMAGE_NAME:$IMAGE_TAG -f $DOCKERFILE $EXTRA_ARGS .
docker push $IMAGE_NAME:$IMAGE_TAG