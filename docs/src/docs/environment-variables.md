# Environment Variables

For each Meltano installation, if you need to customize environment variables, this is done with the `.env` file that is created with each new installation.

## Flask

The following are the environment variables currently available for customization for Flask.

```bash
# Update your .env file with the following

export FLASK_PROFILE = ""
export FLASK_ENV = ""
```

### AuthLib

These customizations are specific to Flask-Authlib.

```bash
# Update your .env file with the following

# GitLab Client ID
export OAUTH_GITLAB_APPLICATION_ID = ""
# GitLab Client Secret
export OAUTH_GITLAB_SECRET = ""
```

## Meltano

The following are the environment variables currently available for customization for Meltano.

```bash
# Update your .env file with the following
export MELTANO_LOG_PATH = ""
export MELTANO_UI_URL = ""
```

## SQL Alchemy Database

The following are the environment variables currently available for customization for Flask.

```bash
# Update your .env file with the following
export MELTANO_API_DATABASE_URI = "YOUR_DATABASE_URI"
```
