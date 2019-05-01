# Environment Variables

For each Meltano installation, if you need to customize environment variables, this is done with the `.env` file that is created with each new installation.

## Flask

The following are the environment variables currently available for customization for Flask.

Update your `.env` file in your project directory with the desired customizations.

```bash
export FLASK_PROFILE = ""
export FLASK_ENV = ""
```

### AuthLib

These variables are specific to [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/#) and work with [OAuth authentication with GitLab](https://docs.gitlab.com/ee/integration/oauth_provider.html).

Update your `.env` file in your project directory with the desired customizations.

```bash
# GitLab Client ID
export OAUTH_GITLAB_APPLICATION_ID = ""
# GitLab Client Secret
export OAUTH_GITLAB_SECRET = ""
```

For more information on how to get these from your GitLab application, check out the [integration docs from GitLab](https://docs.gitlab.com/ee/integration/gitlab.html).

## Meltano

The following are the environment variables currently available for customization for Meltano.

Update your `.env` file in your project directory with the desired customizations.

```bash
# The directory where the Meltano logs will be generated
export MELTANO_LOG_PATH = ""
# The URL where the web app will be located when working locally in development
# since it provides the redirect after authentication.
# Not require for production
export MELTANO_UI_URL = ""
```

## SQL Alchemy Database

The following are the environment variables currently available for customization for Flask.

Update your `.env` file in your project directory with the desired customizations.

```bash
# Your database URI
export MELTANO_API_DATABASE_URI = "YOUR_DATABASE_URI"
```
