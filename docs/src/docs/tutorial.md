# Quick Start

Now that you have successfully installed Meltano, creating a new Meltano project is very simple. Once we initialize a new project on the command line, the rest of your work will take place in our web-based user interface.

## Create Your First Project

Run this command in your terminal to initialize a new project:

```bash
meltano init PROJECT_NAME
```

:::tip
For those new to the command line, your PROJECT_NAME should not have spaces in the name and should use dashes instead. For example, "my project" will not work; but "my-project" will.
:::

Creating a project also created a new directory with the name you gave it. Change to the new directory with this command:

```bash
cd PROJECT_NAME
```

Now that you are inside your project directory, start Meltano with this command:

```bash
meltano ui
```

Meltano is now running, so you can start adding data sources and building dashboards. Open your Internet browser and visit  [http://localhost:5000](http://localhost:5000)



## Connect Data Sources

When you visit the [http://localhost:5000](http://localhost:5000), you should see:

![Meltano UI with Carbon API initial loading screen](/screenshots/meltano-ui-carbon-tutorial-output.png)

From this screen, you can select data source(s) Meltano should ingest into your project using [Plugins](/docs/plugins.html)