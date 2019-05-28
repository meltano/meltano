# Quick Start

Now that you have successfully installed Meltano, creating a new Meltano project is very simple. The Meltano CLI offers you a simple command to initialize a new project:

```bash
meltano init PROJECT_NAME
```

:::tip
For those new to the command line, your PROJECT_NAME should not have spaces in the name and should use dashes instead. For example, "my project" will not work; but "my-project" will.
:::

Navigate into the new directory created for your project:

```bash
cd PROJECT_NAME
```

To start Meltano on your local server:

```bash
meltano ui
```

Meltano is now running locally, and you can start adding data and building dashboards at [http://localhost:5000](http://localhost:5000)

--