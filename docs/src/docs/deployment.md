# Cloud Installation

This section provides step-by-step guides for deploying Meltano on various cloud environments. Currently, we provide detailed intructions for:

- [DigitalOcean One-Click Installer](/docs/deployment.html#digitalocean-marketplace)
- [Amazon Web Services (AWS)](/docs/deployment.html#amazon-web-services-aws)

We are working toward one-click installers, and will update this page as soon as those become available. In the meantime, Meltano can be deployed locally or to the cloud using these instructions.

## DigitalOcean Marketplace

DigitalOcean provides a simple container for spinning up a server where Meltano can be deployed to the Cloud.

<div class="embed-responsive embed-responsive-16by9">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/cfegedH8_VE" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

### Instructions

1. Go to <a :href="$site.themeConfig.data.digitalOceanUrl">Meltano in the DigitalOcean Marketplace</a>

2. Select `Create Meltano Droplet`

3. If you are not logged in already, you will be asked to login, or create a new DigitalOcean account

4. By default, your droplet will come with the following settings that you can customize if desired

- **Image:** Meltano
- **Plan:** Starter - Standard
  - \$40/mo (8GB / 4 CPUs, 160 GB / SSD disk, 5 TB transfer)
- **Datacenter:** A default datacenter region (depending your location)
- **Number of Droplets:** 1 Droplet
- **Backups:** Not enabled by default

5. Add authentication to your droplet via SSH

6. Click `Create Droplet`

Once your Droplet is created, it will have its own IP address displayed in the DigitalOcean user interface.

![Screenshot showing IP address](/images/digitalocean-one-click/01-dooc.jpeg)

7. Visit your Meltano instance at port 5000, like so: `http://{YOUR_IP_ADDRESS}:5000`

Now that you've got your Meltano instance up and running, visit our [Getting Started Guide](/docs/getting-started.html#connect-a-data-source) to connect some data sources and start building your data pipelines and dashboards!

::: info
Looking to customize your DigitalOcean Droplet build and configuration? Please follow the instructions in our [Advanced Tutorial: Manually Creating a DigitalOcean Droplet](/tutorials/manual-digitalocean-droplet.html).
:::

## Amazon Web Services (AWS)

::: warning Prerequisites
This guide assumes that you have a functioning Docker image where your Meltano project is already bundled with the Meltano installation. To track this issue, follow [meltano#624](https://gitlab.com/meltano/meltano/issues/624).
:::

In this section, we will be going over how you can deploy a Meltano Docker image to AWS.

### Setting Up Elastic Container Service (ECS)

1. Login to [AWS Console](https://console.aws.amazon.com)
1. Search for [ECS](https://console.aws.amazon.com/ecs) and click on the link

![](/screenshots/aws-ecs.png)

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

### Review service properties

![](/screenshots/aws-ecs-review-service.png)

1. Verify that the properties are as follows:

- **Service name**: meltano-service
- **Number of desired tasks**: 1
- **Security group**: Automatically create new
- **Load balancer type**: None

1. Click `Next` to move on to the next step

### Configure Your Cluster

The main configuration here is the **Cluster name**. We provide a suggestion below, but feel free to name it as you wish.

- **Cluster name**: meltano-cluster
- **VPC ID**: Automatically create new
- **Subnets**: Automatically create new

### Review Cluster Configuration

After you click `Next`, you will have the opportunity to review all of the properties that you set. Once you confirm that the settings are correct, click `Create` to setup your ECS.

You should now see a page where Amazon prepares the services we configured. There will be spinning icons on the right of each service that will live update as it finished. Once you see everything has setup properly, you're cluster has been successfully deployed!

### Final steps

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

### Configure network access

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
