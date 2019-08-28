# Deployment

In this section provides step-by-step guides for deploying Meltano on various environments. We are working toward one-click installers, and will update this page as soon as those become available. In the meantime, Meltano can be deployed to locally or to the cloud using these instructions.

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

Now that you are inside your virtual environment, follow the [Meltano installation instructions](http://localhost:8080/docs/installation.html#installing-meltano)

Initialize Meltano:
```bash
meltano init meltano
```

Launch the Meltano UI on your server:
```bash
cd meltano
meltano ui
```

::: tip
When you run `meltano ui` you will be prompted to view the Meltano UI at http://localhost:5000, however *this will not work for DigitalOcean Droplets* because they are hosted in the cloud. 

Instead, use the IP address of your DigitalOcean Droplet and port 5000. This will be something like: http://157.230.231.206:5000
:::
