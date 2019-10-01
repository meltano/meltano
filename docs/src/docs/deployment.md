# Cloud Installation

This section provides step-by-step guides for deploying Meltano on various cloud environments. Currently, we provide detailed intructions for:

- [DigitalOcean](/docs/deployment.html#digitalocean-droplets)
- [Amazon Web Services (AWS)](/docs/deployment.html#amazon-web-services-aws)

We are working toward one-click installers, and will update this page as soon as those become available. In the meantime, Meltano can be deployed locally or to the cloud using these instructions.

## DigitalOcean Droplets

DigitalOcean provides a simple container for spinning up a server where Meltano can be deployed to the Cloud. You will need to create an account with DigitalOcean, if you don't have one already. 

We are actively working on a one-click installer for DigitalOcean ([Meltano Issue #926](https://gitlab.com/meltano/meltano/issues/926))

### Creating Your Droplet

From the "Create" dropdown menu in DigitalOcean, choose "Droplets"

For "Choose an Image" select Ubuntu

Choose your plan (the lowest cost "Standard" option is great if you setting this up for the first time) and make any other selections (the defaults are all fine).

Click "Create Droplet" and wait until the progress bar completes. Congratulations, you now have a DigitalOcean Droplet!

### Logging Into Your Droplet

Click on the three-dot dropdown menu to the right of your Droplet's name and select "Access console" to launch the web-based command line. You will be prompted to use your login of "root" and the password that was emailed to you (or SSH key, if you chose that option). Once you enter your username *root* and password (from the email) you will be prompted to change the password to something more secure.

You can also connect to your Droplet using SSH,  from the command line:

```bash
ssh root@YOUR_DROPLET_IP_ADDRESS
```

### Requirements 

Your new server will not have any of [Meltano's requirements](/docs/installation.html#requirements) installed by default, so you will need to install them.

#### Python

Your Ubuntu image will not come with Python 3.6+ set as the sysyem wide version by default, so you will need to complete the following steps.

Get the most updated version of all packages:
```bash
apt-get update
```

And then install Python:
```bash
apt install python
```

Now, if you run `python --version`, you will see the system wide version is 2.7.15+ but Meltano requires 3.6+. Now we need to update the system wide version we want to be using with the command: 

```bash
update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1
```

To confirm the version is now correct, run `python --version` again
```bash
python --version
#Python 3.6.8
```

#### pip

Next up, we need to install our package manager, pip.

```bash
apt install python3-pip
```

#### Virtual Environment

Now that you have Python configured system wide and pip installed, we'll use pip to install your virtual environment management tools:

```bash
pip3 install virtualenv 
```

And then install it with:
```bash
apt-get install python3-venv
```

::: warning
You may be tempted to create your DigitalOcean Droplet without a virtual environment, but due to Python-related installation issues and locked down dependencies for Meltano we *highly recommend* that you take advantage of the virtual environment.
:::

Create a directory where you want your virtual environments to be saved:
```bash
mkdir virtualenvs
```

Then create a new virtual environment inside that directory:
```bash
python -m venv ~/virtualenvs/meltano
```

Activate the virtual environment using:
```bash
source ~/virtualenvs/meltano/bin/activate
```

#### Installing Meltano on your DigitalOcean Droplet

Now that you are inside your virtual environment, follow the [Meltano installation instructions](/docs/installation.html#installing-meltano)

Initialize Meltano:
```bash
meltano init YOUR_PROJECT_NAME
```

Launch the Meltano UI on your server:
```bash
cd YOUR_PROJECT_NAME
meltano ui
```

::: tip
When you run `meltano ui` you will be prompted to view the Meltano UI at http://localhost:5000, however *this will not work for DigitalOcean Droplets* because they are hosted in the cloud. 

Instead, use the IP address of your DigitalOcean Droplet and port 5000.
:::

#### Doing More with Droplets

You can also install PostgreSQL to your DigitalOcean Droplet, and then use that database when you configure the Postgres target. DigitalOcean [provides installation instructions here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04).

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