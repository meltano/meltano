# Environment Variables

For each Meltano installation, if you need to customize environment variables, this is done with the `.env` file that is created with each new installation.

## Anonymous Usage Data

By default, Meltano shares anonymous usage data with the Meltano team using Google Analytics. We use this data to learn about the size of our user base and the specific Meltano features they are (not yet) using, which helps us determine the highest impact changes we can make in each weekly release to make Meltano even more useful for you and others like you.

If you'd prefer to use Meltano _without_ sending the team this kind of data, you can disable tracking entirely using one of these methods:

- When creating a new project, pass `--no_usage_stats` to `meltano init`:

  ```bash
  meltano init PROJECT_NAME --no_usage_stats
  ```

- In an existing project, disable the `send_anonymous_usage_stats` setting in the `meltano.yml` file:

  ```bash
  send_anonymous_usage_stats: false
  ```

- To disable tracking in all projects in one go, set the `MELTANO_DISABLE_TRACKING` environment variable to `True`:

  ```bash
  # Add to `~/.bashrc`, `~/.zshrc`, etc, depending on the shell you use:
  export MELTANO_DISABLE_TRACKING=True
  ```

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

## Log Path

To change the directory where Meltano logs will be generated, update your `.env` in your project directory with the following configuration:

```bash
# The directory where the Meltano logs will be generated
export MELTANO_LOG_PATH = ""
```
