---
title: Tutorial Part 1 - Extract Data
description: Part 1 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 3
---
Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern E(t)LT stack.

We're going to take data from a "source", namely GitLab, and extract a list of projects, the authors, messages and so on.
To test that this part works, we will dump the data into JSON files.
In Part 2, we will then place this data into a PostgreSQL database.

We'll assume you have [Meltano installed](/getting-started/installation) already. You can tell Meltano is installed and which version by running ``` meltano version```

![Meltano Version](images/part1/gif_meltano_version.gif)


This tutorial is written using meltano >= v2.0.0.

If you don't have a GitLab account to follow along, you could either exchange the commands for a different tap, like GitHub or PostgreSQL, or you create a free GitLab account. You will also need a [personal access token to your GitLab account](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) which you can create under "Edit Profile > "Access Tokens" > .

<div class="notification is-success">
    <p>If you're having trouble throughout this tutorial, you can always head over to the <a href="https://meltano.com/slack">Slack channel</a> to get help.</p>
</div>

## Create Your Meltano Project
Step 1 is to create a new [Meltano project](/concepts/project) that (among other things)
will hold the [plugins](/concepts/plugins) that implement the details of our E(t)LT pipeline.


1. Navigate to the directory that you'd like to hold your Meltano projects.

2. Initialize a new project in a directory of your choosing using [`meltano init`](/reference/command-line-interface#init):

   ```bash
   meltano init my-meltano-project
   ```

![Meltano Init](images/part1/gif_meltano_init.gif)

   This action will create a new directory with, among other things, your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file). Your file will look something like this:

   ```yml
   version: 1
   default_environment: dev
   project_id: u3u5u4ueudufhfh4h4h5ddkjh
   environments:
   - name: dev
   - name: staging
   - name: prod
   ```

1. Navigate to the newly created project directory:

   ```bash
   cd my-meltano-project
   ```

## Add an Extractor to Pull Data from a Source

Now that you have your very own Meltano project, it's time to add [plugins](/concepts/plugins) to it. We're going to add an extrator for GitLab to get our data. An [extractor](/concepts/plugins#extractors) is responsible for pulling data out of any data source.

1.  Add the GitLab extractor

    ```bash
    $ meltano add extractor tap-gitlab
    ```
![Meltano Version](images/part1/gif_meltano_add_extr.gif)

    This will add the new plugin to your [`meltano.yml` project file](/concepts/project#plugins):

    ```yml
    plugins:
    extractors:
      - name: tap-gitlab
        variant: meltanolabs
        pip_url: git+https://github.com/MeltanoLabs/tap-gitlab.git
    ```


1.  Test that the installation was successful by calling [`meltano invoke`](/reference/command-line-interface#invoke):

    ```bash
    $ meltano invoke tap-gitlab --help
    ```
    If you see the extractor's help message printed, the plugin was definitely installed successfully.
    ![Meltano Tap Help](images/part1/gif_meltano_invoke_tg_help.gif)


### Configure the Extractor

The GitLab tap requires [configuration](/guide/configuration) before it can start extracting data.

1. The simplest way to configure a new plugin in Meltano is using the mode `interactive`:

   ```bash
   $ meltano config tap-gitlab set --interactive
   ```
2. Follow the prompts to step through all available settings, the ones you'll need to fill out are projects, start_date and your private_token.

![Meltano Version](images/part1/gif_meltano_config_interact.gif)

  This will add the non-sensitive configuration to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

  ```yml
  environments:
    - name: dev
      config:
        plugins:
          extractors:
            - name: tap-gitlab
              config:
                projects: meltano/meltano meltano/tap-gitlab
                start_date: "2021-10-01T00:00:00Z"
  ```

  Sensitive configuration (like `private_token`) will instead be stored in your project's [`.env` file](/concepts/project#env) so that it will not be checked into version control.

3. Double check the config by running [`meltano config tap-gitlab`](/reference/command-line-interface#config):

   ```bash
   meltano config tap-gitlab
   ```
![Meltano Version](images/part1/gif_meltano_config_show.gif)


### Select Entities and Attributes to Extract

Now that the extractor has been configured, it'll know where and how to find your data, but won't yet know which specific entities and attributes (tables and columns) you're interested in.

By default, Meltano will instruct extractors to extract all supported entities and attributes, but we're going to [select specific ones for this tutorial](/guide/integration#selecting-entities-and-attributes-for-extraction). 

1. Find out what entities and attributes are available, using [`meltano select --list --all`](/reference/command-line-interface#select):

   ```bash
   meltano select tap-gitlab --list --all
   ```
  ![Meltano Version](images/part1/gif_meltano_select_all.gif)


1. select the entities and attributes for extraction using [`meltano select`](/reference/command-line-interface#select):

   ```bash
   meltano select tap-gitlab commits id
   meltano select tap-gitlab commits project_id
   meltano select tap-gitlab commits created_at
   meltano select tap-gitlab commits author_name
   meltano select tap-gitlab commits message

   # Exclude matching attributes of all entities
   meltano select tap-gitlab --exclude "*" "*_url"
   ```

   As you can see in the example, entity and attribute identifiers can contain wildcards (`*`) to match multiple entities or attributes at once.

   This will add the [selection rules](/concepts/plugins#select-extra) to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

   ```yml
   plugins:
     extractors:
       - name: tap-gitlab
         variant: meltanolabs
         pip_url: git+https://github.com/MeltanoLabs/tap-gitlab.git
   environments:
     - name: dev
       config:
         plugins:
           extractors:
             - name: tap-gitlab
               config:
                 projects: meltano/meltano meltano/tap-gitlab
                 start_date: "2022-03-01T00:00:00Z"
               select:
                 - commits.id
                 - commits.project_id
                 - commits.created_at
                 - commits.author_name
                 - commits.message
                 - tags.*
                 - "!*.*_url"
   ```

   Note that exclusion takes precedence over inclusion, always.

1. Run [`meltano select --list`](/reference/command-line-interface#select) to double-check your selection:

   ```bash
   meltano select tap-gitlab --list
   ```

## Add a dummy loader to dump the data into JSON
To test that the extraction process works, we add a JSON target. 

1. Add the JSON targt using ```meltano add loader target-jsonl```.
![Meltano Version](images/part1/gif_meltano_add_loader_jsonl.gif)


This target requires zero configuration, it just outputs the data into a timestamped ```jsonl``` file.

## Do a test run to verify the extraction process works

Now that [your Meltano project](#create-your-meltano-project), [extractor](#add-an-extractor-to-pull-data-from-a-source), and [dummy loader](#add-a-loader-to-send-data-to-a-destination) are set up, we can test run the extraction process.

There's just one step here: run your newly added extractor and jsonl loader in a pipeline using [`meltano run`](/reference/command-line-interface#run):

```bash
$ meltano run tap-gitlab target-jsonl
```
![Meltano Version](images/part1/gif_meltano_run.gif)

You should see data flowing from your source into the jsonl file.
You can verify that it worked by looking inside the newly created file called ```output/commits.jsonl```. 
## Next Steps

Next, head over to [Part 2: Loading extracted data into a target (currently inside the large Getting Started Tutorial)](/getting-started/#add-a-loader-to-send-data-to-a-destination).