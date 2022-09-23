---
title: Part 3 - Inline Transformations, E(t)L
description: Part 3 - If you're ready to get started with Meltano and run an EL[T] pipeline with a data source and destination of your choosing, you've come to the right place!
layout: doc
weight: 4
---


Let’s learn by example.

Throughout this tutorial, we’ll walk you through the creation of a end-to-end modern E(t)LT stack.

In parts 1 & 2, we extracted data from GitHub and loaded it into a (local) PostgreSQL database.

Before diving into full-fledged transformations & dbt, we're going to do light-weight, so-called "inline transformations" to clean up the data before storing them anywhere. We're going to import more information from GitHub, including the author details, then use an inline transformation, also called a stream map, to remove the email addresses we get from GitHub by default.

<div class="notification is-success">
    <p>If you're having trouble throughout this tutorial, you can always head over to the <a href="https://meltano.com/slack">Slack channel</a> to get help.</p>
</div>

## Select the author data from GitHub
Just as in Part 1, you can use the [`meltano select`](/reference/command-line-interface#select) command to select additional data from the source. We're simply going to select all "commits" data:

```bash
meltano select tap-github commits "*"
```

This will add the following line to your project file:
```yaml
      extractors:
      - name: tap-github
        select:
        - commits.url # <== technically not necessary anymore, but no need to delete
        - commits.sha # <== technically not necessary anymore, but no need to delete
        - commits.* # <== new data.
```

You can test that the new data is extracted by using `meltano invoke`:

<div class="termy">
```console
$ meltano invoke tap-github
2022-09-22T07:36:52.985090Z [info     ] Environment 'dev' is active
{"type": "STATE", "value":  [...]}
INFO Starting sync of repository: sbalnojan/meltano-example-el
---> 100%
{"type": "SCHEMA", "stream": "commits", [...]

INFO METRIC: {"type": "timer", "metric":  [...]

{"type": "RECORD", "stream": "commits", "record": {"sha": "c771a832720c0f87b3ce53ac12bdcbf742df4e3d", "commit": {"author": {"name": "Horst", "email":
[...]
"sbalnojan/meltano-example-el"}, "time_extracted": "2022-09-22T07:37:06.289545Z"}

...[many more records]...

{"type": "STATE", "value": {"bookmarks": {"sbalnojan/meltano-example-el": {"commits": {"since": "2022-09-22T07:37:06.289545Z"}}}}}
´´´
</div>

## Installing the transform-field mapper
To add inline transformations, we need a new plugin. We're going to use the mapper "transform-field". To add this plugin, use the `meltano add mapper` command:

<div class="termy">
```console
$ meltano add mapper transform-field

Added mapper 'transform-field' to your Meltano project
Variant:        transferwise (default)
Repository:     https://github.com/transferwise/pipelinewise-transform-field
Documentation:  https://hub.meltano.com/mappers/transform-field

Installing mapper 'transform-field'...
---> 100%
Installed mapper 'transform-field'

To learn more about mapper 'transform-field', visit https://hub.meltano.com/mappers/transform-field
</div>

We're now going to add two mappings to this mapper.

## Adding a emails-hidden mapping
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
            type: "MASK-HIDDEN"
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
            type: "MASK-HIDDEN"
```
These lines define one transformation. We target the stream named `commits`, and within it the field named `commit`. We then use the field paths to navigate to the two emails we know are contained within this message and set the type to `MASK-HIDDEN` to hide the values.

## Run the data integration (E(t)L) pipeline
Now we're ready to run the data integration process with these modifications again. To do so, we'll need to clean up first, since we already ran the EL process in part 1. The primary key is still the same and as such the ingestion would fail.

Drop the table inside your local postgres by running

```sql
DROP TABLE tap_github.commits
```

Next we clean up the state Meltano stores to remember the runs. Use `meltano state list` to find out which state you want to clear and then run `meltano state clear X` to clear it:
<div class="termy">
```console
$ meltano state list
2022-09-22T07:29:12.907427Z [info     ] Found state from 2022-09-22 07:13:55.526950.
dev:tap-github-to-target-postgres
dev:tap-github-to-target-jsonl
$ meltano state clear dev:tap-github-to-target-postgres
2022-09-22T07:29:56.033502Z [info     ] Environment 'dev' is active
This will clear state for the job. Continue? [y/N]:
$ y
```

</div>
<br />
Now we can run the E(t)L process again using the `meltano run`command:

<div class="termy">

```console
$ meltano run tap-github hide-github-mails target-postgres
2022-09-20T13:16:13.885045Z [warning  ] No state was found, complete import.
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
If everything was configured correctly, you should now see your data flow from your source into your destination! Check the database to see how the "email" fields now both contain the values "hidden".


## Next Steps

Next, head over to [Part 4, to add transformations to your ingestion process](/getting-started/part4).

<script src="/js/termynal.js"></script>
<script src="/js/termy_custom.js"></script>
