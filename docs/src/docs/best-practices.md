# Best Practices

## How to use sub pipelines to effectively create a DAG like architecture

An example of this can be seen in the [gitlab-ci.yml](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/.gitlab-ci.yml#L251) which is being used to trigger the gitlab-qa project. This will trigger a [`SCRIPT_NAME`:`trigger-build`](https://gitlab.com/gitlab-org/gitlab-ce/blob/master/scripts/trigger-build) which has the API calls written in Ruby, for which we can use Python. From there the sky is the limit.

## Managing API requests and limits

Many of the SaaS sources have various types of API limits, typically a given quota per day. If you are nearing the limit of a given source, or are iterating frequently on your repo, you may need to implement some additional measures to manage usage.

### Reducing API usage by review apps

One of the easiest ways to reduce consumption of API calls for problematic ELT sources is to make that job manual for branches other than `master`. This way when iterating on a particular branch, this job can be manually run only if it specifically needs to be tested.

We don't want the job on `master` to be manual, so we will need to create two jobs. The best way to do this is to convert the existing job into a template, which can then be referenced so we don't duplicate most of the settings.

For example take a sample Zuora ELT job:

```yaml
zuora:
  stage: extract
  image: registry.gitlab.com/meltano/meltano-elt/extract:latest
  script:
    - set_sql_instance_name
    - setup_cloudsqlproxy
    - envsubst < "elt/config/environment.conf.template" > "elt/config/environment.conf"
    - python3 elt/zuora/zuora_export.py
    - stop_cloudsqlproxy
```

The first thing to do would to convert this into an anchor, and preface the job name with `.` so it is ignored:

```yaml
.zuora: &zuora
  stage: extract
  image: registry.gitlab.com/meltano/meltano-elt/extract:latest
  script:
    - set_sql_instance_name
    - setup_cloudsqlproxy
    - envsubst < "elt/config/environment.conf.template" > "elt/config/environment.conf"
    - python3 elt/zuora/zuora_export.py
    - stop_cloudsqlproxy
```

Next, we can define two new jobs. One for `master` and another manual job for any review branches:

```yaml
zuora_prod:
  <<: *zuora
  only:
    - master

zuora_review:
  <<: *zuora
  only:
    - branches
  except:
    - master
  when: manual
```

## Pipeline configuration

Data integration stages are configurable using `Project variables` for the CI/CD pipeline. The following variables may help you control what needs to run:

- `EXTRACT_SKIP`: either `all` (to skip the `extract` stage) or job names, like `marketo,zendesk,zuora` to be skipped from the pipeline.
- `UPDATE_SKIP`: either `all` (to skip the `update` stage) or job names, like `sfdc_update`.

## Stored procedures

We don't use stored procedures because they are hard to keep under version control.