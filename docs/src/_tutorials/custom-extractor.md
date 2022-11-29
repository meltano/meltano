---
title: Create a Custom Extractor
description: Learn how to use Meltano to create a custom data extractor.
layout: doc
weight: 2
---

As much as we'd like to support all the data sources out there, we'll need your help to get there. If you find a data source that Meltano doesn't support right now, it might be time to get your hands dirty.

## What Are Custom Extractors?

Custom extractors are scripts or tools that source data from unconventional data sources like a custom database or a SaaS API like Appwrite and present it in a form that can be loaded into the desired target sink. The term “custom” here means the extractor isn’t a native part of the tool.

![Extraction and Loading Tasks in ELT Pipeline](https://i.imgur.com/ObUogVY.png)

A custom extractor must present the extracted data in a form that the tool can use to load it into the target sink like a data warehouse.

Singer is a commonly used tool for extracting data, which serves as the specification for implementing data extractors and loaders.

Singer refers to extractor scripts as taps and loader scripts as targets. If you use Singer for your ELT needs, a custom extractor is basically a Singer tap written for your organization’s needs.

These Singer taps and targets can be cumbersome to run manually so the easiest way to run them is as Meltano extractor/loader plugins. Meltano’s EL features handle all of the Singer complexity of configuration, stream discovery, and state management.

## How to Create a Custom Extractor

The following steps will demonstrate how to implement a custom extractor to extract data from a JSON placeholder REST API to a JSONL file using Meltano and the Meltano SDK. You can check out the complete custom extractor code on this [GitHub repo](https://github.com/vicradon/tap-jsonplaceholder).

There a few prerequisites that you need before continuing. The [first step](#1-installing-dependencies) details how you can install these dependencies.

1. [Python3](https://www.python.org/downloads/) for running Python-based scripts
2. [Pip3](https://pypi.org/project/pip/#files) for installing pipx
3. [Poetry](https://python-poetry.org/) for dependency management in your custom extractor
4. [Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) for installing the template repository

## 1. Installing the Dependencies

You can install Python3 from the [official website](https://www.python.org/downloads/). Python usually comes packaged with a package installer known as pip.

You can verify that pip is installed by running the below command:

```
pip3 --version
```

Any version number above 20 should be able to install pipx. You can then run the command below to install pipx, meltano, cookiecutter, and poetry.

```
pip3 install pipx

pipx ensurepath

source ~/.bashrc

pipx install meltano

pipx install cookiecutter

pipx install poetry
```

Pipx is a wrapper around pip that simplifies the process of installing Python programs that need to be added to path (e.g., Meltano).

You will use cookiecutter to clone the Meltano SDK template repo for implementing a custom extractor.

Poetry serves as the dependency manager for the project. If you have used npm before, poetry serves a similar purpose but for Python projects.


## 2. Create a Project Using the Cookiecutter Template

Run the following command to create the project files from the cookiecutter template:

```
cookiecutter https://github.com/meltano/sdk --directory="cookiecutter/tap-template"
```

After running the above command, you will be prompted to configure your project.

- Type `jsonplaceholder` as your source name
- Then input your first name and last name.
- You can leave the tap_id and library name as the default suggested names.
- For the stream type, you should select REST, and Custom or N/A for the auth method.
- Finally, you can choose to add a CI/CD template or not. It doesn’t really matter in this case.

```
source_name [MySourceName]: jsonplaceholder

admin_name [FirstName LastName]: <Your First Name, Your Last Name>

tap_id [tap-jsonplaceholder]:

library_name [tap_jsonplaceholder]:

Select stream_type:

1 - REST

2 - GraphQL

3 - SQL

4 - Other

Choose from 1, 2, 3, 4 [1]: 1

Select auth_method:

1 - API Key
2 - Bearer Token
3 - Basic Auth
4 - OAuth2
5 - JWT
6 - Custom or N/A
Choose from 1, 2, 3, 4, 5, 6 [1]: 6

Select include_cicd_sample_template:

1 - GitHub
2 - None (Skip)
Choose from 1, 2 [1]:
```

The result of the above command is a new directory `tap-jsonplaceholder` that contains boilerplate code for developing your tap and also a `meltano.yml` file that you can use to test your custom extractor.

You can view the cookiecutter template in [cookiecutter directory in the Meltano SDK repository](https://github.com/meltano/sdk/tree/main/cookiecutter).

## 3. Install the Custom Extractor Python dependencies Using Poetry

Change directory into the json-placeholder tap directory, and install the python dependencies using poetry:

```bash
cd tap-jsonplaceholder

# [Optional] but useful if you need to debug your custom extractor
poetry config virtualenv.in-project true

poetry install
```

See [Debug A Custom Extractor](https://docs.meltano.com/guide/debugging-custom-extractor) to learn more about the optional Poetry step above.

## 4. Configure the Custom Extractor to Consume Data from the Source

To configure your custom extractor to consume data from the JSON placeholder, you need to set the **API_URL** and the **streams** that will be replicated.

Open the file ```tap-jsonplaceholder/tap_jsonplaceholder/tap.py``` and replace its content with the content below:

```python
"""jsonplaceholder tap class."""

from typing import List

from singer_sdk import Tap, Stream

from singer_sdk import typing as th # JSON schema typing helpers

from tap_jsonplaceholder.streams import (

jsonplaceholderStream,

CommentsStream

)


STREAM_TYPES = [

CommentsStream

]


class Tapjsonplaceholder(Tap):

"""jsonplaceholder tap class."""

name = "tap-jsonplaceholder"



def discover_streams(self) -> List[Stream]:

"""Return a list of discovered streams."""

return [stream_class(tap=self) for stream_class in STREAM_TYPES]

```

Then replace the content of ```tap-jsonplaceholder/tap_jsonplaceholder/streams.py``` with the content below:


```python
"""Stream type classes for tap-jsonplaceholder."""

from singer_sdk import typing as th # JSON Schema typing helpers

from tap_jsonplaceholder.client import jsonplaceholderStream


class CommentsStream(jsonplaceholderStream):
    primary_keys = ["id"]
    path = '/comments'
    name = "comments"
    schema = th.PropertiesList(
        th.Property("postId", th.IntegerType),
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("email", th.StringType),
        th.Property("body", th.StringType),
    ).to_dict()
```

The ```tap.py``` file defines the tap settings and the available streams, which is the comments stream in this case. You can find the available stream types in the STREAM_TYPES array.

The ```streams.py``` file configures the comments stream to use the /comments path and also sets the properties of the extracted fields.

Finally, change the url_base in the ```tap-jsonplaceholder/tap_jsonplaceholder/client.py``` file to https://jsonplaceholder.typicode.com.


```python
...

class jsonplaceholderStream(RESTStream):

"""jsonplaceholder stream class."""



# TODO: Set the API's base URL here:

url_base = "https://jsonplaceholder.typicode.com"

...
```

## 5. Install The Newly Created Tap

Navigate to your project root directory on your shell and run the following command:

```bash
meltano install

meltano add loader target-jsonl
```

This command installs your newly created tap, tap-jsonplaceholder, and a loader, target-jsonl, to the default Meltano project. It also creates an output directory where the extracted data will be loaded.

Execute the command below to run an ELT pipeline that replicates data from the REST API to JSONL files:

```bash
meltano run tap-jsonplaceholder target-jsonl
```
You can inspect the output directory for the extracted JSON data.

Use the command below to get the first five lines of the extracted comments JSON file:

```bash
head -n 5 output/comments.jsonl
```

You should see the following:

```
{"postId": 1, "id": 1, "name": "id labore ex et quam laborum", "email": "Eliseo@gardner.biz", "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium"}

{"postId": 1, "id": 2, "name": "quo vero reiciendis velit similique earum", "email": "Jayne_Kuhic@sydney.com", "body": "est natus enim nihil est dolore omnis voluptatem numquam\net omnis occaecati quod ullam at\nvoluptatem error expedita pariatur\nnihil sint nostrum voluptatem reiciendis et"}

{"postId": 1, "id": 3, "name": "odio adipisci rerum aut animi", "email": "Nikita@garfield.biz", "body": "quia molestiae reprehenderit quasi aspernatur\naut expedita occaecati aliquam eveniet laudantium\nomnis quibusdam delectus saepe quia accusamus maiores nam est\ncum et ducimus et vero voluptates excepturi deleniti ratione"}

{"postId": 1, "id": 4, "name": "alias odio sit", "email": "Lew@alysha.tv", "body": "non et atque\noccaecati deserunt quas accusantium unde odit nobis qui voluptatem\nquia voluptas consequuntur itaque dolor\net qui rerum deleniti ut occaecati"}

{"postId": 1, "id": 5, "name": "vero eaque aliquid doloribus et culpa", "email": "Hayden@althea.biz", "body": "harum non quasi et ratione\ntempore iure ex voluptates in ratione\nharum architecto fugit inventore cupiditate\nvoluptates magni quo et"}
```

## Interacting with your new plugin

Now that your plugin is installed and configured, you are ready to interact with it using Meltano.

Use `meltano invoke` to run your plugin in isolation:

```bash
meltano invoke tap-my-custom-source
```

You can also use the `--discover` flag to see details about the supported streams:

```bash
meltano invoke tap-my-custom-source --discover
```

You can also use [`meltano select`](/getting-started#select-entities-and-attributes-to-extract)
to parse your `catalog` and list all available entities and attributes:

```bash
meltano select --list --all
```

## Add the Custom Extractor Plugin to Your Meltano Project

Once you have tested your custom extractor, by installing and running it in the custom extractor repository, you might want to add it to a separate Meltano project.

### If You Don't Have An Existing Meltano Project

Navigate to the parent directory of your custom extractor and run the following command:

```bash
meltano init
```
The above command will prompt you to enter a project name. You should enter a name like meltano-demo. Afterward, navigate into the newly created project using the below command:

```bash
cd meltano-demo
```

Meltano exposes each custom extractor configuration in the plugin definition, located in the [`meltano.yml` project file](/concepts/project#meltano-yml-project-file).

To test the custom extractor as part of your Meltano project, you will need to add your custom extractor configuration in the `meltano.yml` file for your project.

There are two ways you can do this:


## 1. Use The Meltano Add Command

Run the command below to add the extractor as a custom extractor not hosted on MeltanoHub registry:

```bash
meltano add --custom extractor tap-jsonplaceholder
```

You will be prompted to input the namespace URL. Choose ```tap-jsonplaceholder```.

Also, choose ```-e …/tap-jsonplaceholder``` as the pip_url since you are working with a local extractor project. This should be the full path to your custom extractor.

Go with the default executable name.

You can leave the capabilities and settings fields blank for now. The command will install the custom extractor to your Meltano project.

```
Added extractor 'tap-jsonplaceholder' to your Meltano project

Installing extractor 'tap-jsonplaceholder'...

Installed extractor 'tap-jsonplaceholder'
```

### Add a JSONL target

Run the command below to add the JSONL loader that will contain the extracted data stream:

```bash
meltano add loader target-jsonl
```

### Run an ELT Pipeline That Loads Data into a JSONL File

The following command will run an ELT pipeline that loads data into a JSONL file:

```bash
meltano run tap-jsonplaceholder target-jsonl
```

### Inspect the Loaded Data in the Outputs Directory

Run the following command to get the first five lines of the comments JSONL file:

```bash
head -n 5 output/comments.jsonl
```

## 2. Edit Your Existing Meltano.yml file

In your existing `meltano.yml`:

```yml
# ...
plugins:
  extractors:
    # Insert a new entry:
    - name: tap-my-custom-source
      namespace: tap_my_custom_source
      # Installs the plugin from a local path
      # in 'editable' mode (https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs).
      # Can point to '.' if it's in the same directory as `meltano.yml`
      pip_url: -e /path/to/tap-my-custom-source
      # Name of custom tap that will be invoked.
      # Can be found in the pyproject.toml of your custom tap under CLI declaration
      executable: tap-my-custom-source
      capabilities:
        # For a reference of plugin capabilities, see:
        # https://docs.meltano.com/reference/plugin-definition-syntax#capabilities
        - state
        - catalog
        - discover
      config:
        # Configured values:
        username: me@example.com
        start_date: '2021-01-01'
      settings:
        - name: username
        - name: password
          kind: password
        - name: start_date
          # Default value for the plugin:
          value: '2010-01-01T00:00:00Z'
  loaders:
    # your loaders here:
    - name: target-jsonl
      variant: andyh1203
      pip_url: target-jsonl
    # ...
```

<div class="notification is-info">
  <p>You can further customize the appearance of your custom extractor using the following options:</p>
  <ul>
    <li>`label`</li>
    <li>`logo_url`</li>
    <li>`description`</li>
  </ul>
</div>

Any time you manually add new plugins to `meltano.yml`, you will need to rerun the
[install](/reference/command-line-interface#install) command:

```bash
meltano install
```

## Plugin Settings

When creating a new custom extractor plugin, you'll often have to expose some settings to the user so that Meltano can generate the correct configuration to run your custom extractor.

To properly expose and configure your settings, you'll need to define them:

- **name**: Identifier of this setting in the configuration.
  The name is the most important field of a setting, as it defines how the value will be passed down to the underlying component.
  Nesting can be represented using the `.` separator.

  - `foo` represents the `{ foo: VALUE }` in the output configuration.
  - `foo.a` represents the `{ foo: { a: VALUE } }` in the output configuration.
- **kind**: Represent the type of value this should be, (e.g. `password` for sensitive values or `date_iso8601` for dates).
- **value** (optional): Define a default value for the plugin's setting.

### Passing sensitive setting values

_**It is best practice not to store sensitive values directly in `meltano.yml`.**_

Note in our example above, we provided values directly for `username` and `start_date` but we did not enter a value
for password. This was to avoid storing sensitive credentials in clear text within our source code. Instead, make sure the setting `kind` is set to `password` and then
run [`meltano config <plugin> set password <value>`](/getting-started#configure-the-extractor). You can also set the matching environment variable for this
setting by running `export TAP_MY_CUSTOM_SOURCE_PASSWORD=<value>`.

You may use any of the following to configure setting values (in order of precedence):

- Environment variables
- `config` section in the plugin
- `value` of the setting's definition

## Publishing to the world

Once you've built your tap and it is providing you the data you need, we hope you will consider
sharing it with the world! We often find that community
members who benefit from your tap also may contribute back their own improvements in
the form of pull requests.

### Publish to PyPI

If you've built your tap using the SDK, you can take advantage of the streamlined
[`poetry publish`](https://python-poetry.org/docs/cli/#publish) command to publish
your tap directly to PyPI.

1. Create an account with [PyPI](https://pypi.org).
2. Create a PyPI API token for use in automated publishing. (Optional but recommended.)
3. Run `poetry build` from within your repo to build.
4. Run `poetry publish` to push your latest version to the PyPI servers.

### Test a `pip` install

We recommend using pipx to avoid dependency conflicts:

```bash
pip3 install pipx
pipx ensurepath
python -m pipx install tap-my-custom-source
```

After restarting your terminal, this should also work without the `python -m` prefix:

```bash
pipx install tap-my-custom-source
```

Or if you don't want to use pipx:

```bash
pip3 install tap-my-custom-source
```

If you have gotten this far... _**Congrats!** You are now a proud Singer tap developer!_

### Make it discoverable

Once you have your tap published to PyPI, consider
[making it discoverable](/contribute/plugins#making-a-custom-plugin-discoverable)
for other users of Meltano.

### Updates for production use

Once your repo is installable with pip, you can reference this in your `meltano.yml` file with three quick steps:

1. Add a `pip_url` property to your `extractor` definition, for example `pip_url: tap-my-custom-source`.
   - _Alternatively, you can also install the latest from your git repo directly using this syntax:
     `pip_url: git+https://github.com/myusername/tap-my-custom-source@main`_
2. Replace `/path/to/tap-my-custom-source.sh` with just the executable name: `tap-my-custom-source`.
3. Rerun `meltano install` to use the version from pip in place of the local test version.

## References

- [SDK for Singer Taps and Targets](https://sdk.meltano.com)
- [Singer Spec](https://hub.meltano.com/singer/spec)
- [Meltano Blog - How to Build a Custom Extractor](https://meltano.com/blog/how-to-build-a-custom-extractor-with-meltano/)
