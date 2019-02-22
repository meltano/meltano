---
sidebarDepth: 2
---

# Tutorials

## Quick Start

First time using Meltano? No worries. We got you covered with tutorials that will guide you through how Meltano works. Let's get started!

### Carbon API

This tutorial is perfect if your goal is to get Meltano up and running as quickly as possible.

For this tutorial, we will be working with the [Carbon Intensity API](https://carbon-intensity.github.io/api-definitions/) which is free and does not require any authentication.

### Initialize Your Project

To get started, navigate to a directory, in your terminal, where you want your Meltano project to be installed and run the following commands:

```bash
# Initialize a new project with a folder called carbon
meltano init carbon

# Change directory into your new carbon project
cd carbon

# Let's see what extractors and loaders are available
meltano discover all

# Run elt (extract, load, transform) with an id of your choice and the extractor and
# loader we just added without the need to transform the data
meltano elt tap-carbon-intensity target-sqlite
```

Congratulations! You have just loaded all the data from Carbon Intensity API into your local warehouse.

### Interact with Your Data in the Web App

Now that your data is ready to be analyzed, it's time to start up the web app! Go back into your terminal and run the following command:

```bash
# Start up the Meltano UI web application!
$ meltano ui
```

This will start a local web server at [http://localhost:5000](http://localhost:5000). 

When you visit the URL, you should see:

![](/screenshots/01-meltano-ui.png)

---
#### Run a Simple Analysis on Your Data

Meltano uses custom data files wth the extension `.m5o` that define the structure for your data.

In your project directory, you will see some examples under the `model` folder: `carbon.model.m5o`.




Next, we'll ensure our models are valid so Meltano Analyze can properly generate queries for us:

- By default the Model page is loaded, same as clicking the Model button (upper-left)
  - Every time you go to this page, the models are linted, synced, and the UI updates with an error if a model is invalid. Otherwise you'll see the "Passed" indicator meaning you're clear to analyze.

Lastly, we'll query and explore the data:

- Navigate to Model > Region (Model dropdown)
- Open Region accordion
  - Toggle Columns and Aggregates buttons to generate SQL query
  - Click Run button to query
- Open Charts accordion and explore the data!

## Advanced Content

Looking for more advanced tutorials? You can look forward to the following tutorials in the future:

- Salesforce
- GitLab Runners
- Google Analytics
