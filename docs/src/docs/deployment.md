# Deployment

## Amazon Web Services (AWS)

::: warning Prerequisites
This guide assumes that you have a functioning Docker image where your Meltano project is already bundled with the Meltano installation. To track this issue, follow [meltano#624](https://gitlab.com/meltano/meltano/issues/624).
:::

In this section, we will be going over how you can deploy a Meltano Docker image to AWS.

### Setting Up Elastic Container Service (ECS)

1. Login to [AWS Console](https://console.aws.amazon.com)
1. Search for [ECS](https://console.aws.amazon.com/ecs) and click on the link

![](/screenshots/aws-ecs.png)

#### Define container and task

![](/screenshots/aws-ecs-getting-started.png)

1. We will create a new _Container definition_ by clicking on the `Configure` button in the **custom** card
1. Fill out the form with the following data:
  - **Container name**: Meltano
  - **Image**: YOUR_DOCKER_IMAGE_URL
    - Examples:
      - docker.io/namespace/image-name:tag
      - registry.gitlab.com/namespace/project/image-name:tag
  - **Memory Limits (MiB)**: Soft limit 1024
  - **Port mappings**: 
    - 5000/tcp (meltano)
    - 5010/tcp (airflow)

1. Click `Update` button to finish setting up your container defintion
1. Click `Edit` next to the _Task defintion_ heading
1. Update the form with the following:
  - **Task definition name**: meltano-run
  - **Network mode**: awsvpc
  - **Task execution role**: ecsTaskExecutionRole
  - **Compatibilities**: FARGATE
  - **Task memory**: 1GB (1024)
  - **Task CPU**: 0.25 vCPU (256)
1. Click `Next` to move to the next step

#### Review service properties 

![](/screenshots/aws-ecs-review-service.png)

1. Verify that the properties are as follows:
  - **Service name**: meltano-service
  - **Number of desired tasks**: 1
  - **Security group**: Automatically create new
  - **Load balancer type**: None
1. Click `Next` to move on to the next step

#### Configure your cluster

The main configuration here is the **Cluster name**. We provide a suggestion below, but feel free to name it as you wish.

  - **Cluster name**: meltano-cluster
  - **VPC ID**: Automatically create new
  - **Subnets**: Automatically create new

#### Review cluster configuration

After you click `Next`, you will have the opportunity to review all of the properties that you set. Once you confirm that the settings are correct, click `Create` to setup your ECS.

You should now see a page where Amazon prepares the services we configured. There will be spinning icons on the right of each service that will live update as it finished. Once you see everything has setup properly, you're cluster has been successfully deployed!

#### Final steps

![](/screenshots/aws-ecs-final-steps.png)

1. Open the page with your cluster
1. Click on the _Tasks_ tab
1. You should see a task that has a status of `RUNNING` for _Last Status_
1. Click on the _Task ID_ link (e.g., 0b35dea-3ca..)
1. Under _Network_, you can find the URL for your instance under _Public IP_ (e.g., 18.18.134.18)
1. Open a new tab in your browser and visit this new URL on port 5000 (e.g., http://18.18.134.18:5000)

::: tip
The IP address can be mapped to a domain using Route53. We will be writing up a guide on how to do this. You can follow along at [meltano#625](https://gitlab.com/meltano/meltano/issues/625).
:::

#### Configure network access

::: tip
This section is only necessary if you do not have a Security Group that allows for port 5000,5010 inbound.
:::

Once you complete the cluster setup, you should be brought to the detail page for the service. You should be default on a tab called _Details_ with a _Network Access_ section.

1. Navigate to the _Details_ tab
1. Under _Network Access_, click on the link next to _Security Groups_ (e.g., sg-f0dj093dkjf10)
1. This should open a new tab with your security group
1. Navigate to the _Inbound Rules_ tab on the bottom of the page
1. Click `Edit Rules`
1. Delete any existing rules
1. Click `Add Rule` with the following properties:
  - **Type**: Custom TCP Rule
  - **Protocol**: TCP
  - **Port Range**: 5000
  - **Source**: Custom 0.0.0.0/0
1. Click "Add Rule" with the following properties:
  - **Type**: Custom TCP Rule
  - **Protocol**: TCP
  - **Port Range**: 5010
  - **Source**: Custom 0.0.0.0/0
1. Click `Save rules`

## Coming Next

- Creating a data warehouse for Meltano
- Running ELT in the Cloud
- Growing and Scaling Meltano
- Running Meltano with AWS EC2
- Using AWS Lambda with Meltano
