---
sidebar: auto
---

# tap-gitlab Tutorial

For this tutorial, our goal will be to get [tap-gitlab](https://gitlab.com/meltano/tap-gitlab) integrated with your Meltano project. 

## Prerequisites

- Meltano
- GitLab account
- Basic command line knowledge

## Setup

Let's start by initializing a new project! Navigate to your desired directory and run:

```bash
# Start a new Meltano project called tutorial-tap-gitlab
meltano init tutorial-tap-gitlab

# Once the setup is complete, navigate into your project
cd tutorial-tap-gitlab
```

### Add Loader

Next, we will be configuring the warehouse where your data will live. In this tutorial, we will use Postgres; but you can substitute this for another loader if desired.

```bash
# Add target-postgres to your project
meltano add loader target-postgres 
```

If you check your `.env` file, you should see the following configuration already populated:

```bash
export PG_PASSWORD=warehouse
export PG_USERNAME=warehouse
export PG_ADDRESS=localhost
export PG_SCHEMA=meltano
export PG_PORT=5502
export PG_DATABASE=warehouse
```

Once you verify that your database is setup correctly, it's time to start working with `tap-gitlab`!

### Add Extractor

Adding `tap-gitlab` to your project is just as easy as the loader.

```bash
meltano add extractor tap-gitlab
```

Once the installation is successful, you need to open your `.env` file and add the following to it:

```bash
export GITLAB_API_URL=https://gitlab.com/api/v4
export GITLAB_API_TOKEN=
export GITLAB_API_PROJECTS=
export GITLAB_API_GROUPS=
export GITLAB_API_START_DATE=
```

Next, we will start configuring your extractor so you can fetch data!

## Configuration

### GitLab API Token

In order to access GitLab's API to fetch data, we must get a personal access token that will authenticate you with the server. This is very simple to do:

<video controls style="max-width: 100%">
  <source src="/screenshots/personal-access-token.mov">
</video>

1. Navigate to your [profile's access tokens](https://gitlab.com/profile/personal_access_tokens).

2. Fill out the personal access token form with the following properties:
  - **Name:** tap-gitlab-tutorial 
  - **Expires:** _leave blank unless you have a specific reason to expire the token_
  - **Scopes:** 
    - api

3. Click on `Create personal access token` to submit your request.

4. You should see your token appear at the top of your screen.

5. Copy and paste the token into your `.env` file under the property `GITLAB_API_TOKEN`. It should look something like this:

```bash
...
export GITLAB_API_TOKEN=I8vxHsiVAaDnAX3hA
...
```

### Gitlab API Projects

This property allows you to scope the project that the service fetches, but it is completely optional. If this is left blank, the extractor will try to fetch all projects that it can grab.

If you want to configure this, the format for it is `group/project`. Here are a couple examples:

- `meltano/meltano` - https://gitlab.com/meltano/
- `meltano/tap-salesforce` - https://gitlab.com/meltano/tap-salesforce

For this tutorial, we will scope our data sample to only include the Meltano project to make things faster. So now we will populate the `GITLAB_API_PROJECTS` property as follows:

```bash
...
export GITLAB_API_PROJECTS=meltano/meltano
...
```

### GitLab API Groups

This property allows you to scope data that the extractor fetches to only the desired group(s). The group name can generally be found at the root of a repo URL. If this is left blank, the extractor will try to fetch all groups within GitLab.

For example, `https://www.gitlab.com/meltano/tap-gitlab` has a group of `Meltano`. This can be confirmed as well by visiting `https://gitlab.com/meltano` and noting the Group ID below the header.

![Group ID verification example](/screenshots/group-header-example.png)

For this tutorial, we will also scope the data to reduce the size of data being fetched. So we will configure the property `GITLAB_API_GROUPS` with the Meltano group.

```bash
...
export GITLAB_API_GROUPS=meltano
...
```

### GitLab API Start Date

This property allows you to configure where you want your data set to start from. Otherwise, if left blank, it will try fetch the entire history of the groups or projects if they are defined.

Similar to the previous examples, we will limit the scope of data being fetched in order to shorten the download time, so let's configure the start date to the beginning of last month.

```bash
...
# The date format is ISO-8601
export GITLAB_API_START_DATE=2019-05-01T00:00:00Z
...
```

## Running tap-gitlab

Now that everything is setup, we can run our extractor with the following command:

```bash
PG_SCHEMA='tap_gitlab' meltano elt tap-gitlab target-postgres
```

::: tip
You might notice that we are declaring a specific Postgres schema at the beginning of the command. This is to ensure that the data tables do not collide with other data sources and is considered a best practice.
:::

You should now see the data being fetched and your Postgres database properly populated once it is complete. Congratulations!
