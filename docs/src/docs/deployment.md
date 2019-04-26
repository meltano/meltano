# Deployment

## Amazon Web Services (AWS)

In this section, we will be going over how you can deploy a Meltano Docker image to AWS.

1. Login to [AWS Console](https://console.aws.amazon.com)
1. Search for [Elastic Container Service (ECS)](https://console.aws.amazon.com/ecs) and click on the link

### Define container and task

1. We will create a new "Container definition" by clicking on the `Configure` button in the "custom" card
1. Fill out the form with the following data:
  - **Container name**: Meltano
  - **Image**: 292927715491.dkr.ecr.us-east-2.amazonaws.com/meltano
  - **Memory Limits (MiB)**: Soft limit 128
  - **Port mappings**: 80 tcp
1. Click `Update` button to finish setting up your container defintion
1. Click `Next` to move to the next step

### Review service properties 

1. Verify that the properties are as follows:
  - **Service name**: meltano-service
  - **Number of desired tasks**: 1
  - **Security group**: Automatically create new
  - **Load balancer type**: None
1. Click `Next` to move on to the next step

### Configure your cluster

The main configuration here is the `Cluster name`. We provide a suggestion below, but feel free to name it as you wish.

  - **Cluster name**: meltano
  - **VPC ID**: Automatically create new
  - **Subnets**: Automatically create new

### Finish creating your cluster

After you click `Next`, you will have the opportunity to review all of the properties that you set. Once you confirm that the setttings are correct, click `Create` to setup your ECS.

You should now see a page where Amazon prepares the services we configured. There will be spinning icons on the right of each service that will live update as it finished.

Once you see everything has setup properly, congratulations on deploying a Meltano Docker image with ECS!

## Meltano UI

Meltano UI consist of a Flask API and a Vue.js front-end application, both included in the `meltano` package.

To run Meltano in production, we recommend using [gunicorn](http://docs.gunicorn.org/en/stable/install.html).

First, install gunicorn:

```bash
$ pip install gunicorn
```

You can then start Meltano UI:

> Note: this is an example invocation of gunicorn, please refer to
> the [gunicorn documentation](http://docs.gunicorn.org/en/stable/settings.html) for more details.

```bash
;; ALWAYS run Meltano UI in production mode when it is accessible externally
$ export FLASK_ENV=production

;; start gunicorn with 4 workers, alternatively you can use `$(nproc)`
$ gunicorn -c python:meltano.api.wsgi.config -w 4 meltano.api.wsgi:app
```
