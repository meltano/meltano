---
sidebar: auto
metaTitle: Meltano Tutorial - Create a Meltano Digital Ocean Droplet
description: Learn how to create a Digital Ocean Droplet ready to use to host a Meltano instance.
lastUpdatedSignificantly: 2020-02-20
---

# Manually Creating a DigitalOcean Droplet

From the "Create" dropdown menu in DigitalOcean, choose "Droplets"

For "Choose an Image" select Ubuntu

Choose your plan (the lowest cost "Standard" option is great if you setting this up for the first time) and make any other selections (the defaults are all fine).

Click "Create Droplet" and wait until the progress bar completes. Congratulations, you now have a DigitalOcean Droplet!

## Logging Into Your Droplet

Click on the three-dot dropdown menu to the right of your Droplet's name and select "Access console" to launch the web-based command line. You will be prompted to use your login of "root" and the password that was emailed to you (or SSH key, if you chose that option). Once you enter your username _root_ and password (from the email) you will be prompted to change the password to something more secure.

You can also connect to your Droplet using SSH, from the command line:

```bash
ssh root@YOUR_DROPLET_IP_ADDRESS
```

## Requirements

Your new server will not have any of [Meltano's requirements](/docs/installation.html#requirements) installed by default, so you will need to install them.

### Python

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

### pip3

Next up, we need to install our package manager, pip.

```bash
apt install python3-pip
```

### Virtual Environment

Now that you have Python configured system wide and pip3 installed, we'll use pip3 to install your virtual environment management tools:

```bash
pip3 install virtualenv
```

And then install it with:

```bash
apt-get install python3-venv
```

::: warning
You may be tempted to create your DigitalOcean Droplet without a virtual environment, but due to Python-related installation issues and locked down dependencies for Meltano we _highly recommend_ that you take advantage of the virtual environment.
:::

Create a directory where you want your virtual environments to be saved:

```bash
mkdir venv
```

Then create a new virtual environment inside that directory:

```bash
python -m venv venv/.venv/meltano
```

Activate the virtual environment using:

```bash
source venv/.venv/meltano/bin/activate
```

### Installing Meltano on your DigitalOcean Droplet

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
When you run `meltano ui` you will be prompted to view the Meltano UI at http://localhost:5000, however _this will not work for DigitalOcean Droplets_ because they are hosted in the cloud.

Instead, use the IP address of your DigitalOcean Droplet and port 5000.
:::

### Doing More with Droplets

You can also install PostgreSQL to your DigitalOcean Droplet, and then use that database when you configure the Postgres target. DigitalOcean [provides installation instructions here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04).
