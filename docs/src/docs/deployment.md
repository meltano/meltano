# Deployment

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
