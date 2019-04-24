# Deployment

When it is time to deploy Meltano to a production environment, you can find instructions for the respective applications and workflows below.

## Meltano UI

Meltano UI consist of a Flask API and a Vue.js front-end application, which are both included in the `meltano` package. In other words, the Flask API is not exposed at a project level and any customizations needed must be done at the package level.

To run Meltano in production, we recommend using [gunicorn](http://docs.gunicorn.org/en/stable/install.html) for setting up your HTTP Server.

First, install gunicorn:

```bash
$ pip install gunicorn
```

You can then start Meltano UI:

::: warning Note
This is an example invocation of gunicorn, please refer to
the [gunicorn documentation](http://docs.gunicorn.org/en/stable/settings.html) for more details.
:::

```bash
# ALWAYS run Meltano UI in production mode when it is accessible externally
$ export FLASK_ENV=production

# Start gunicorn with 4 workers, alternatively you can use `$(nproc)`
$ gunicorn -c python:meltano.api.wsgi.config -w 4 meltano.api.wsgi:app
```


