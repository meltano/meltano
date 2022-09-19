---
title: Tutorial Part 1 - Extract Data
description: Part 1 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 3
---


Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern E(t)LT stack. In this part, we're going to start with the data extraction process.

We're going to take data from a "source", namely GitHub, and extract a list of commits to one repository.

To test that this part works, we will dump the data into JSON files.
In Part 2, we will then place this data into a PostgreSQL database.

We'll assume you have [Meltano installed](/getting-started/installation) already. You can tell Meltano is installed and which version by running ``` meltano version```

<div id="termynal" data-termynal id="termy1">
    <span data-ty="input">meltano --version</span>
    <span data-ty>meltano, version 2.6.0</span>
</div>

This tutorial is written using meltano >= v2.0.0.

If you don't have a GitHub account to follow along, you could either exchange the commands for a differe tap, like GitLab or PostgreSQL, or you can create a free GitHub account. You will also need a [personal access token to your GitHub account](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

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
<br>
  <div id="termynal" data-termynal id="termy2">
      <span data-ty="input">meltano init my-new-project</span>
      <span data-ty>Created my-new-project</span>
      <span data-ty>Creating project files...
    my-new-project/
    <br> |-- .meltano
    <br> |-- meltano.yml
    <br> |-- README.md
    <br> |-- requirements.txt
    <br> |-- output/.gitignore
    <br> |-- .gitignore
    <br> |-- extract/.gitkeep
    <br> |-- load/.gitkeep
    <br> |-- transform/.gitkeep
    <br> |-- analyze/.gitkeep
    <br> |-- notebook/.gitkeep
    <br> |-- orchestrate/.gitkeep</span>
  <span data-ty>Creating system database...  Done!</span>
  <span data-ty>... Project my-new-project has been created!
  <br><br>
  Meltano Environments initialized with dev, staging, and prod.
  <br>To learn more about Environments visit: https://docs.meltano.com/concepts/environments
  <br><br>
  Next steps:
  <br>  cd my-new-project
  <br>  Visit https://docs.meltano.com/getting-started#create-your-meltano-project to learn where to go from here</span>
  </div>
<br>

   This action will create a new directory with, among other things, your [`meltano.yml` project file](/concepts/project#meltano-yml-project-file). Your file will look something like this:

   ```yml
   version: 1
   default_environment: dev
   project_id: <unique-GUID>
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

Now that you have your very own Meltano project, it's time to add [plugins](/concepts/plugins) to it. We're going to add an extrator for GitHub to get our data. An [extractor](/concepts/plugins#extractors) is responsible for pulling data out of any data source.

1.  Add the GitHub extractor

```bash
$ meltano add extractor tap-github
```
<br>
  <div id="termynal" data-termynal id="termy3">
      <span data-ty="input">meltano add extractor tap-github</span>
<span data-ty>2022-09-19T09:32:05.162591Z [info     ] Environment 'dev' is active</span>
<span>Added extractor 'tap-github' to your Meltano project
<br>Variant:        singer-io (default)
<br>Repository:     https://github.com/singer-io/tap-github
<br>Documentation:  https://hub.meltano.com/extractors/tap-github
<br><br>
<br>Installing extractor 'tap-github'...</span>
<span data-ty>Installed extractor 'tap-github'
<br><br>
To learn more about extractor 'tap-github', visit https://hub.meltano.com/extractors/tap-github</span>
</div>
<br>

This will add the new plugin to your [`meltano.yml` project file](/concepts/project#plugins):

```yml
plugins:
extractors:
  - name: tap-github
    variant: singer-io
    pip_url: tap-github
```


1.  Test that the installation was successful by calling [`meltano invoke`](/reference/command-line-interface#invoke):

```bash
$ meltano invoke tap-github --help
```

If you see the extractor's help message printed, the plugin was definitely installed successfully.

<br>
  <div id="termynal" data-termynal id="termy4">
      <span data-ty="input">meltano invoke tap-github --help</span>
<span data-ty>2022-09-19T09:32:05.162591Z [info     ] Environment 'dev' is active</span>
<br><span data-ty>usage: tap-github [-h] -c CONFIG [-s STATE] [-p PROPERTIES] [--catalog CATALOG] [-d]
<br><br>
<br>options:
<br>  -h, --help            show this help message and exit
<br>  -c CONFIG, --config CONFIG
<br>                        Config file
<br>  -s STATE, --state STATE
<br>                        State file
<br>  -p PROPERTIES, --properties PROPERTIES
<br>                        Property selections: DEPRECATED, Please use --catalog instead
<br>  --catalog CATALOG     Catalog file
<br>  -d, --discover        Do schema discovery </span>
</div>

### Configure the Extractor

The GitHub tap requires [configuration](/guide/configuration) before it can start extracting data.

1. The simplest way to configure a new plugin in Meltano is using the mode `interactive`:

```bash
$ meltano config tap-github set --interactive
```
2. Follow the prompts to step through all available settings, the ones you'll need to fill out are repositories, start_date and your private_token.


<br>
  <div id="termynal" data-termynal id="termy5">
      <span data-ty="input">meltano config tap-github set --interactive</span>
<span data-ty>2022-09-19T09:32:05.162591Z [info     ] Environment 'dev' is active</span>
<br><span data-ty>
 Configuring Extractor 'tap-github'
<br>[...]                                                                                                                        <br>1. access_token: Personal access token used to authenticate with GitHub. The token can be...
<br>2. repository: Space-separated list of repositories. Each repository must be prefaced b...
<br>3. start_date: Defines how far into the past to pull data for the provided repositories.                                                                                                                <br><br>
To learn more about extractor 'tap-github' and its settings, visit https://hub.meltano.com/extractors/tap-github
<br><br>

Loop through all settings (all), select a setting by number (1 - 3), or exit (e)? [all]: </span>
<span data-ty="input">1</span>
<span data-ty> [...]Description:
Personal access token used to authenticate with GitHub. The token can be generated by going to the Personal Access Token
 settings page.  </span>
 <span data-ty>New value: </span><span data-ty="input">  </span>
 <span data-ty>Repeat for confirmation:</span> <span data-ty="input">  </span>
<span data-ty> [... other 2 values...] </span>
</div>


This will add the configuration to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

  ```yml
  environments:
    - name: dev
      config:
        plugins:
          extractors:
            - name: tap-github
              config:
                access_token: YOUR_TOKEN
                start_date: 2022-01-01
                repository: sbalnojan/meltano-lightdash
  ```


3. Double check the config by running [`meltano config tap-github`](/reference/command-line-interface#config):

```bash
meltano config tap-github
```
<br>
  <div id="termynal" data-termynal id="termy6">
      <span data-ty="input">meltano config tap-github</span>
<span data-ty>2022-09-19T11:26:22.888257Z [info     ] Environment 'dev' is active</span>
<span data-ty>2022-09-19T11:26:23.573556Z [info     ] The default environment (dev) will be ignored for `meltano config`. To configure a specific Environment, please use option `--environment=[]`.</span>
<span data-ty>
{
<br>  "access_token": "[YOUR_TOKEN]",
<br>  "repository": "sbalnojan/meltano-lightdash",
<br>  "start_date": "2022-01-01"
<br>
}</span>
</div>

### Select Entities and Attributes to Extract

Now that the extractor has been configured, it'll know where and how to find your data, but won't yet know which specific entities and attributes (tables and columns) you're interested in.

By default, Meltano will instruct extractors to extract all supported entities and attributes, but we're going to [select specific ones for this tutorial](/guide/integration#selecting-entities-and-attributes-for-extraction).

1. Find out what entities and attributes are available, using [`meltano select YOUR_TAP --list --all`](/reference/command-line-interface#select):

```bash
meltano select tap-github --list --all
```
<br>
  <div id="termynal" data-termynal id="termy7">
      <span data-ty="input">meltano select tap-github --list</span>
<span data-ty>2022-09-19T10:59:43.554214Z [info     ] Environment 'dev' is active</span>
<span data-ty>Legend:
<br>        selected
<br>        excluded
<br>        automatic
<br>
<br>Enabled patterns:
<br>        *.*
<br>
<br>Selected attributes:
<br>        [selected ] assignees._sdc_repository
<br>        [automatic]
<br>        [...]
<br>        [selected ] commits.comments_url
<br>        [selected ] commits.commit
<br>        [selected ] commits.commit.author
<br>        [...]
<br>        [selected ] teams.repositories_url
<br>        [selected ] teams.slug
<br>        [selected ] teams.url</span>
</div>

1. Select the entities and attributes for extraction using [`meltano select`](/reference/command-line-interface#select):

```bash
meltano select tap-github commits url
meltano select tap-github commits sha
```

   This will add the [selection rules](/concepts/plugins#select-extra) to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

  ```yml
  version: 1
  default_environment: dev
  environments:
  - name: dev
    config:
      plugins:
        extractors:
        - name: tap-github
          select:
          - commits.url
          - commits.sha
  - name: staging
  - name: prod
  project_id: blub-58f363d3-d5c0-43d1-a182-e0967b3fb58b
  plugins:
    extractors:
    - name: tap-github
      variant: singer-io
      pip_url: tap-github
      config:
        access_token: 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
        start_date: 2022-01-01
        repository: sbalnojan/meltano-lightdash
  ```


1. Run [`meltano select --list`](/reference/command-line-interface#select) to double-check your selection:

```bash
meltano select tap-github --list
```

## Add a dummy loader to dump the data into JSON
To test that the extraction process works, we add a JSON target.

1. Add the JSON targt using ```meltano add loader target-jsonl```.



<br>
  <div id="termynal" data-termynal id="termy8" class="termy">
      <span data-ty="input">meltano add loader target-jsonl</span>
<span data-ty>2022-09-19T13:47:42.389423Z [info     ] Environment 'dev' is active</span>
<span data-ty>To add it to your project another time so that each can be configured differently,
add a new plugin inheriting from the existing one with its own unique name:
<br>        meltano add loader target-jsonl--new --inherit-from target-jsonl
<br>
<br>Installing loader 'target-jsonl'...
<br>Installed loader 'target-jsonl'
<br>
<br>To learn more about loader 'target-jsonl', visit https://hub.meltano.com/loaders/target-jsonl
</span>
</div>



This target requires zero configuration, it just outputs the data into a ```jsonl``` file.

## Do a test run to verify the extraction process works

Now that [your Meltano project](#create-your-meltano-project), [extractor](#add-an-extractor-to-pull-data-from-a-source), and [dummy loader](#add-a-loader-to-send-data-to-a-destination) are set up, we can test run the extraction process.

There's just one step here: run your newly added extractor and jsonl loader in a pipeline using [`meltano run`](/reference/command-line-interface#run):

```bash
$ meltano run tap-github target-jsonl
```
<br>
  <div id="termynal" data-termynal id="termy9">
      <span data-ty="input">meltano run tap-github target-jsonl</span>
<span data-ty><br>2022-09-19T13:53:36.403099Z [info     ] Environment 'dev' is active
<br>2022-09-19T13:53:41.062802Z [info     ] Found state from 2022-09-19 13:53:17.415907.
<br>2022-09-19T13:53:41.071885Z [warning  ] No state was found, complete import.</span>
<span data-ty><br>2022-09-19T13:53:43.054384Z [info     ] INFO Starting sync of repository: sbalnojan/meltano-lightdash cmd_type=elb consumer=False name=tap-github producer=True stdio=stderr string_id=tap-github
<br>2022-09-19T13:53:43.553171Z [info     ] INFO METRIC: {"type": "timer", "metric": "http_request_duration", "value": 0.4796161651611328, "tags": {"endpoint": "commits", "http_status_code": 200, "status": "succeeded"}} cmd_type=elb consumer=False name=tap-github producer=True stdio=stderr string_id=tap-github
<br>2022-09-19T13:53:43.561190Z [info     ] INFO METRIC: {"type": "counter", "metric": "record_count", "value": 1, "tags": {"endpoint": "commits"}} cmd_type=elb consumer=False name=tap-github producer=True stdio=stderr string_id=tap-github</span>
<span data-ty><br>2022-09-19T13:53:43.735250Z [info     ] Incremental state has been updated at 2022-09-19 13:53:43.734535.
<br>2022-09-19T13:53:43.820467Z [info     ] Block run completed.           block_type=ExtractLoadBlocks err=None set_number=0 success=True</span>
</div>

You should see data flowing from your source into the jsonl file.
You can verify that it worked by looking inside the newly created file called ```output/commits.jsonl```.

  <div id="termynal" data-termynal id="termy10">
      <span data-ty="input">cat output/commits.jsonl</span>
<span data-ty>{"sha": "409bdd601e0531833665f538bccecd0f69e101c0", "url": "https://api.github.com/repos/sbalnojan/meltano-lightdash/commits/409bdd601e0531833665f538bccecd0f69e101c0"}</span>
</div>
## Next Steps

Next, head over to [Part 2: Loading extracted data into a target (currently inside the large Getting Started Tutorial)](/getting-started/#add-a-loader-to-send-data-to-a-destination).

  <script src="/js/termynal.js" data-termynal-container="#termy1|#termy2|#termy3|#termy4|#termy5|#termy6|#termy7|#termy8|#termy9|#termy10"></script>
  <script src="/js/termy_custom.js"></script>
