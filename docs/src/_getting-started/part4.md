---
title: Part 4 - Inline Data Mapping
description: Part 4 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 4
---


Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern ELT stack.

In parts [1](/getting-started/part1), [2](/getting-started/part2), and [3](/getting-started/part3) we built an ELT pipeline. We took all the data from the commits on one repository at GitHub and extracted the authors working on it. However now we realized, we stored a lot of information where we really might want to hide a few of those pieces.

We're going to do light-weight transformations, also called **"inline data mappings"** to clean up the data before storing them anywhere. We will use these inline data mappings to hide all emails inside the JSON blob we receive. In the Meltano world, these data mappings are also called [stream maps](https://sdk.meltano.com/en/latest/stream_maps.html).

<div class="notification is-success">
    <p>If you're having trouble throughout this tutorial, you can always head over to the <a href="https://meltano.com/slack">Slack channel</a> to get help.</p>
</div>


## Installing the transform-field mapper
To add inline data mappings, we need a new plugin. We're going to use the mapper "transform-field". To add this plugin, use the `meltano add mapper` command:

<div class="termy">
```console
$ meltano add mapper transform-field

Added mapper 'transform-field' to your Meltano project
Variant:        transferwise (default)
Repository:     https://github.com/transferwise/pipelinewise-transform-field
Documentation:  https://docs.meltano.com/concepts/plugins#mappers

Installing mapper 'transform-field'...
---> 100%
Installed mapper 'transform-field'

To learn more about mapper 'transform-field', visit https://docs.meltano.com/concepts/plugins#mappers
</div>

We're now going to add two mapping to this mapper.

## Adding an emails-hidden mapping
To add our first mapping, we're going to edit the `meltano.yml` file located inside your root project directory. Modify the block for the `transform-field` mapper as shown below:

```yaml
mappers:
  - name: transform-field
    variant: transferwise
    pip_url: pipelinewise-transform-field
    executable: transform-field
   mappings:
    - name: hide-github-mails
      config:
        transformations:
          - field_id: "commit"
            tap_stream_name: "commits"
            field_paths: ["author/email", "committer/email"]
            type: "HASH"
```
Let's go through this step-by-step

```yaml
mappers:
  [...]
   mappings:
    - name: hide-github-mails
      config:
        transformations:
          [...]
```
These lines define the name "hide-github-mails" as the name of our mapping. We can call the mapping using this name, and ignoring any reference to the actual mapper "transform-field".

```yaml
    [...]
        transformations:
          - field_id: "commit"
            tap_stream_name: "commits"
            field_paths: ["author/email", "committer/email"]
            type: "HASH"
```
These lines define one transformation. We instruct to target the stream "commits", and therein the field "commit". We then use the field paths to navigate to the two emails we know are contained within this message and set the type to "HASH". Using "HASH" means we will still be able to tell whether two emails are the same, but not be able to read the email. They will be replaced with a SHA-256 hash of the email.

## Run the data integration pipeline
Now we're ready to run the data integration process with these modifications again. To do so, we'll need to clean up first, since we already ran the EL process in part 1. The primary key is still the same and as such the ingestion would fail.

Drop the table inside your local postgres by running a docker exec:

```bash
docker exec meltano_postgres psql -U meltano -c 'DROP TABLE tap_github.commits; DROP TABLE analytics.authors;'
```

Now we can run the full process again using the `meltano run`command. We add the parameter --full-refresh to ignore the state Meltano has stored.

<div class="termy">

```console
$ meltano run --full-refresh tap-github hide-github-mails target-postgres dbt-postgres:run
2022-09-20T13:16:15.441183Z [info     ] Performing full refresh, ignoring state left behind by any previous runs.

2022-09-20T13:16:15.441183Z [info     ] INFO Starting sync of repository: [...]

2022-09-20T13:16:15.901789Z [info     ] INFO METRIC: {"type": "timer", "metric": "http_request_duration",[...]
---> 100%
2022-09-20T13:16:15.933874Z [info     ] INFO METRIC: {"type": "counter", "metric": "record_count", "value": 21,[...]

2022-09-20T13:16:16.435885Z [info     ] [...] message=Schema 'tap_github' does not exist. Creating... ...

2022-09-20T13:16:16.632945Z [info     ] ... message=Table '"commits"' does not exist. Creating...

2022-09-20T13:16:16.729076Z [info     ] ...message=Loading 21 rows into 'tap_github."commits"' ...

---> 100%
2022-09-20T13:16:16.864812Z [info     ] ...Loading into tap_github."commits": {"inserts": 21, "updates": 0, "size_bytes": 4641} ...

2022-09-20T13:16:16.885846Z [info     ] Incremental state has been updated at 2022-09-20 13:16:16.885259.

2022-09-20T13:16:16.960093Z [info     ] Block run completed.           ....
```
</div>
<br />
If everything was configured correctly, you should now see your data flow from your source into your destination! Take your favourite SQL tool, connect to the database using the connection details set and check the table `commits` inside the schema `tap_github`. The JSON blob inside the column `commit` should now contain no e-mail adresses but rather the hashed values for both fields.

## Next Steps
There we have it, a complete ELT pipeline with inline data mappings, congratulations!

One last thing for you to do: try to run the following command to celebrate:

```bash
meltano dragon
```

Next, head over to [Part 5, scheduling of jobs](/getting-started/#schedule-pipelines-to-run-regularly).

<script src="/js/termynal.js"></script>
<script src="/js/termy_custom.js"></script>
