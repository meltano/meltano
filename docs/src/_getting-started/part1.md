---
title: Tutorial Part 1 - Extract Data
description: Part 1 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 4
---


Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern ELT stack. In this part, we're going to start with the data extraction process.

We're going to take data from a "source", namely GitHub, and extract a list of commits to one repository.

To test that this part works, we will dump the data into JSON files.
In Part 2, we will then place this data into a PostgreSQL database.

We'll assume you have [Meltano installed](/getting-started/installation) already. You can tell Meltano is installed and which version by running ``` meltano version```

<div class="termy">

```console
$ meltano --version
meltano, version 2.6.0
</div>
<br />
This tutorial is written using meltano >= v2.0.0.

If you don't have a GitHub account to follow along, you could either exchange the commands for a differe tap, like GitLab or PostgreSQL, or you can create a free GitHub account. You will also need a [personal access token to your GitHub account](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).

<div class="notification is-success">
    <p>If you're having trouble throughout this tutorial, you can always head over to the <a href="https://meltano.com/slack">Slack channel</a> to get help.</p>
</div>

## Create Your Meltano Project
Step 1 is to create a new [Meltano project](/concepts/project) that (among other things)
will hold the [plugins](/concepts/plugins) that implement the details of our ELT pipeline.


1. Navigate to the directory that you'd like to hold your Meltano projects.

2. Initialize a new project in a directory of your choosing using [`meltano init`](/reference/command-line-interface#init):

```bash
meltano init my-meltano-project
```
<br>
<div class="termy">

```console
$ meltano init my-new-project
Created my-new-project
Creating project files...
  my-new-project/
   |-- .meltano
   |-- meltano.yml
   |-- README.md
   |-- requirements.txt
   |-- output/.gitignore
   |-- .gitignore
   |-- extract/.gitkeep
   |-- load/.gitkeep
   |-- transform/.gitkeep
   |-- analyze/.gitkeep
   |-- notebook/.gitkeep
   |-- orchestrate/.gitkeep
Creating system database...  Done!
... Project my-new-project has been created!

Meltano Environments initialized with dev, staging, and prod.
To learn more about Environments visit: https://docs.meltano.com/concepts/environments

Next steps:
  cd my-new-project
  Visit https://docs.meltano.com/getting-started#create-your-meltano-project to learn where to go from here.

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
<br />

<div class="termy">

```console
$ meltano add extractor tap-github
2022-09-19T09:32:05.162591Z [info     ] Environment 'dev' is active
Added extractor 'tap-github' to your Meltano project
Variant:        singer-io (default)
Repository:     https://github.com/singer-io/tap-github
Documentation:  https://hub.meltano.com/extractors/tap-github

Installing extractor 'tap-github'...
Installed extractor 'tap-github'

To learn more about extractor 'tap-github', visit https://hub.meltano.com/extractors/tap-github
```
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
<br />
If you see the extractor's help message printed, the plugin was definitely installed successfully.

<div class="termy">

```console
$ meltano invoke tap-github --help
2022-09-19T09:32:05.162591Z [info     ] Environment 'dev' is active
usage: tap-github [-h] -c CONFIG [-s STATE] [-p PROPERTIES] [--catalog CATALOG] [-d]

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config file
  -s STATE, --state STATE
                        State file
  -p PROPERTIES, --properties PROPERTIES
                        Property selections: DEPRECATED, Please use --catalog instead
  --catalog CATALOG     Catalog file
  -d, --discover        Do schema discovery
```
</div>

### Configure the Extractor

The GitHub tap requires [configuration](/guide/configuration) before it can start extracting data.

1. The simplest way to configure a new plugin in Meltano is using the mode `interactive`:

```bash
$ meltano config tap-github set --interactive
```
2. Follow the prompts to step through all available settings, the ones you'll need to fill out are repositories, start_date and your private_token.
<br>
<div class="termy">

```console
$ meltano config tap-github set --interactive
2022-09-19T09:32:05.162591Z [info     ] Environment 'dev' is active
 Configuring Extractor 'tap-github'
[...]                                                                      1. access_token: Personal access token used to authenticate with GitHub. The token can be...
2. repository: Space-separated list of repositories. Each repository must be prefaced b...
3. start_date: Defines how far into the past to pull data for the provided repositories.

To learn more about extractor 'tap-github' and its settings, visit https://hub.meltano.com/extractors/tap-github

Loop through all settings (all), select a setting by number (1 - 3), or exit (e)? [all]:
$ 1
[...]Description:
Personal access token used to authenticate with GitHub. The token can be generated by going to the Personal Access Token
 settings page.
New value:
$
Repeat for confirmation:
$
<[... other 2 values...]
```
</div>
<br />
This will add the configuration to your [`meltano.yml` project file](/concepts/project#plugin-configuration):

  ```yml
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
<div class="termy">

```console
$ meltano config tap-github
2022-09-19T11:26:22.888257Z [info     ] Environment 'dev' is active
2022-09-19T11:26:23.573556Z [info     ] The default environment (dev) will be ignored for `meltano config`. To configure a specific Environment, please use option `--environment=[]`.

{
  "access_token": "[YOUR_TOKEN]",
  "repository": "sbalnojan/meltano-lightdash",
  "start_date": "2022-01-01"
}
```

</div>

### Select Entities and Attributes to Extract

Now that the extractor has been configured, it'll know where and how to find your data, but won't yet know which specific entities and attributes (tables and columns) you're interested in.

By default, Meltano will instruct extractors to extract all supported entities and attributes, but we're going to [select specific ones for this tutorial](/guide/integration#selecting-entities-and-attributes-for-extraction).

1. Find out what entities and attributes are available, using [`meltano select YOUR_TAP --list --all`](/reference/command-line-interface#select):

```bash
meltano select tap-github --list --all
```
<br>
<div class="termy">

```console
$ meltano select tap-github --list
2022-09-19T10:59:43.554214Z [info     ] Environment 'dev' is active
Legend:
        selected
        excluded
        automatic

Enabled patterns:
        *.*

Selected attributes:
        [selected ] assignees._sdc_repository
        [automatic]
        [...]
        [selected ] commits.comments_url
        [selected ] commits.commit
        [selected ] commits.commit.author
        [...]
        [selected ] teams.repositories_url
        [selected ] teams.slug
        [selected ] teams.url
```
</div>

1. Select the entities and attributes for extraction using [`meltano select`](/reference/command-line-interface#select):

```bash
meltano select tap-github commits url
meltano select tap-github commits sha
```
<br />
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
  project_id: YOUR_ID
  plugins:
    extractors:
    - name: tap-github
      variant: singer-io
      pip_url: tap-github
      config:
        access_token: YOUR_TOKEN
        start_date: 2022-01-01
        repository: sbalnojan/meltano-lightdash
  ```


1. Run [`meltano select --list`](/reference/command-line-interface#select) to double-check your selection:

```bash
meltano select tap-github --list
```

## Add a dummy loader to dump the data into JSON
To test that the extraction process works, we add a JSON target.

1. Add the JSON target using ```meltano add loader target-jsonl```.
<br>
<div class="termy">

```console
$ meltano add loader target-jsonl</span>
2022-09-19T13:47:42.389423Z [info     ] Environment 'dev' is active
To add it to your project another time so that each can be configured differently,
add a new plugin inheriting from the existing one with its own unique name:
 &nbsp;&nbsp;&nbsp;&nbsp;meltano add loader target-jsonl--new --inherit-from target-jsonl

Installing loader 'target-jsonl'...
Installed loader 'target-jsonl'

To learn more about loader 'target-jsonl', visit https://hub.meltano.com/loaders/target-jsonl
```
</div>
<br />
This target requires zero configuration, it just outputs the data into a ```jsonl``` file.

## Do a test run to verify the extraction process works

Now that [your Meltano project](#create-your-meltano-project), [extractor](#add-an-extractor-to-pull-data-from-a-source), and [dummy loader](#add-a-loader-to-send-data-to-a-destination) are set up, we can test run the extraction process.

There's just one step here: run your newly added extractor and jsonl loader in a pipeline using [`meltano run`](/reference/command-line-interface#run):

```bash
$ meltano run tap-github target-jsonl
```
<br>
<div class="termy">

```console
$ meltano run tap-github target-jsonl
2022-09-19T13:53:36.403099Z [info     ] Environment 'dev' is active
2022-09-19T13:53:41.062802Z [info     ] Found state from 2022-09-19 13:53:17.415907.
2022-09-19T13:53:41.071885Z [warning  ] No state was found, complete import.
2022-09-19T13:53:43.054384Z [info     ] INFO Starting sync of repository: sbalnojan/meltano-lightdash cmd_type=elb consumer=False name=tap-github producer=True stdio=stderr string_id=tap-github
2022-09-19T13:53:43.553171Z [info     ] INFO METRIC: {"type": "timer", "metric": "http_request_duration", "value": 0.4796161651611328, "tags": {"endpoint": "commits", "http_status_code": 200, "status": "succeeded"}} cmd_type=elb consumer=False name=tap-github producer=True stdio=stderr string_id=tap-github
2022-09-19T13:53:43.561190Z [info     ] INFO METRIC: {"type": "counter", "metric": "record_count", "value": 1, "tags": {"endpoint": "commits"}} cmd_type=elb consumer=False name=tap-github producer=True stdio=stderr string_id=tap-github</span>
2022-09-19T13:53:43.735250Z [info     ] Incremental state has been updated at 2022-09-19 13:53:43.734535.
2022-09-19T13:53:43.820467Z [info     ] Block run completed.           block_type=ExtractLoadBlocks err=None set_number=0 success=True</span>
```
</div>
<br />
You should see data flowing from your source into the jsonl file.
You can verify that it worked by looking inside the newly created file called ```output/commits.jsonl```.


<div class="termy">

```console
$ cat output/commits.jsonl
{"sha": "409bdd601e0531833665f538bccecd0f69e101c0", "url": "https://api.github.com/repos/sbalnojan/meltano-lightdash/commits/409bdd601e0531833665f538bccecd0f69e101c0"}
```

</div>
## Next Steps

Next, head over to [Part 2: Loading extracted data into a target (currently inside the large Getting Started Tutorial)](/getting-started/part2).


   <script src="/js/termynal.js" data-termynal-container="#termy1|#termy2|#termy3|#termy4|#termy5|#termy6|#termy7|#termy8|#termy9|#termy10"></script>
  <script src="/js/termy_custom.js"></script>
