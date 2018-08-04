#!/usr/bin/env python3
import requests
import json
import time
import datetime
import psycopg2
import csv
import logging
import os
import io
import sys

from requests.auth import HTTPBasicAuth
from sqlalchemy import desc
from elt.job import Job, State
from elt.utils import compose, slugify, setup_db
from elt.db import DB
from elt.process import integrate_csv
from elt.schema import schema_apply
from elt.error import Error, ExtractError
from schema import PG_SCHEMA, describe_schema, field_column_name
from config import JOB_VERSION, DATE_MIN, INCREMENTAL_DATE, environment, getPGCreds, getZuoraFields, getObjectList


class DownloadError(Error):
    """Happens when a file cannot be downloaded from the Zuora endpoint."""
    def __init__(self, message, fatal=False):
        super().__init__(message)
        self.fatal = fatal


def item_jobs(item):
    """
    Yields import jobs for a specific item from the following sources:
      - Previous failed jobs
      - Zuora API incremental job
    """
    for job in recover_jobs(item):
        logging.info("Recovering failed job {}".format(job))
        yield job

    # creating the incremental job to send in the pipeline
    job = Job(elt_uri=item_elt_uri(item),
              payload={
                  'zuora_state': 'init',
              })

    logging.info("Retrieving incremental job for {}.".format(item))
    yield job


def recover_jobs(item):
    with DB.session() as session:
        elt_uri = item_elt_uri(item)
        failed_jobs = session.query(Job).filter_by(state=State.FAIL,
                                                   elt_uri=elt_uri).all()

    logging.info("Found {} failed job for {}.".format(len(failed_jobs), elt_uri))
    return failed_jobs


def item_incremental_time(item):
    FORMAT = "%Y-%m-%d %H:%M:%S"

    if INCREMENTAL_DATE is not None:
        logging.info("ZUORA_INCREMENTAL_DATE_OVERRIDE is set: {}".format(INCREMENTAL_DATE))
        return INCREMENTAL_DATE

    with DB.session() as session:
        elt_uri = item_elt_uri(item)
        last_job = session.query(Job).filter_by(state=State.SUCCESS, elt_uri=elt_uri) \
                                     .order_by(desc(Job.started_at)) \
                                     .first()

    date = job_start_date(last_job) or DATE_MIN
    return date.strftime(FORMAT)


def job_start_date(job):
    if not job: return None

    try:
        raw_date = job.payload.get('http_response', {}).get('startTime')
        return datetime.datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S%z")
    except:
        return None


def item_elt_uri(item):
    return "com.meltano.zuora:{}:{}".format(JOB_VERSION, slugify(item))


def create_extract_job(job, item):
    if job.payload['zuora_state'] != 'init':
        return

    url = environment['url']
    headers, data = zuora_query_params(item)

    job.started_at = datetime.datetime.utcnow()
    job.payload.update({
        'query': data
    })
    Job.save(job)

    res = requests.post(url,
                        auth=HTTPBasicAuth(environment['username'], environment['password']),
                        headers=headers,
                        data=data,
                        stream=True)

    result = res.json()
    if result['status'] == 'error':
        raise ExtractError(result['message'])

    job_id = result['id']
    job.payload.update({
        'id': job_id,
        'url': url,
        'zuora_state': 'query',
        'http_response': result,
    })
    Job.save(job)

    return job


def load_extract_job(job, job_id):
    if job.payload['zuora_state'] != 'query':
        return

    params = {
        'auth': HTTPBasicAuth(environment['username'],
                              environment['password']),
        'headers': {'Accept': 'application/json'},
    }

    url = "/".join((environment['url'], "jobs", job_id))
    result = ""
    while True:
        res = requests.get(url, **params)
        result = res.json()
        status = result['batches'][0]['status']

        job.payload['http_response'] = result
        job.payload['zuora_state'] = status
        Job.save(job)
        if status == 'completed':
            # expect to only have 1 batch
            file_id = result['batches'][0]['fileId']
            logging.info("File ID: " + file_id)
            job.payload['file_id'] = file_id
            Job.save(job)
            break
        time.sleep(30)

    return job


def download_file(item, file_id):
    params = {
        'auth': HTTPBasicAuth(environment['username'],
                              environment['password']),
        'headers': {'Accept': 'application/json'},
    }

    filename = "{}.csv".format(item)
    fields = [field_column_name(field) for field in getZuoraFields(item)]

    url = "https://www.zuora.com/apps/api/file/{}".format(file_id)
    res = requests.get(url, **params)

    if res.status_code != requests.codes.ok:
        raise DownloadError("Unable to download the file at {}.".format(url),
                            fatal=res.status_code == requests.codes.not_found)

    def rename_fields(row):
        renamed = dict()
        for col, val in row.items():
            column_name = col.replace("{}.".format(item), "")
            column_name = column_name.replace(".", "")
            column_name = column_name.lower()

            renamed[column_name] = val

        return renamed

    with open(filename, 'w') as file:
        buf = io.StringIO(res.text)
        dr = csv.DictReader(buf, delimiter=',')
        dw = csv.DictWriter(file,
                            delimiter=',',
                            fieldnames=fields,
                            extrasaction='ignore')

        # write the file back ignoring the fields that are not in our schema
        dw.writeheader()
        for row in dr:
            dw.writerow(rename_fields(row))

    return filename


def replace(fieldList):
    for i, v in enumerate(fieldList):
        if v.upper() == 'TRUE':
            fieldList.pop(i)
            fieldList.insert(i, '1')
        if v.upper() == 'FALSE':
            fieldList.pop(i)
            fieldList.insert(i, '0')
        if v == '':
            fieldList.pop(i)
            fieldList.insert(i, None)


def db_write_incremental(item):
    _, _, host, db, _ = getPGCreds()
    #primary_key = 'id'
    #columns = [field_column_name(field) for field in getZuoraFields(item)]
    #update_columns = [col for col in columns if col != primary_key]

    csv_file_name = ".".join((item, "csv"))
    logging.info("[Update] Writing to {}/{}".format(host, db))
    with DB.open() as db:
        integrate_csv(db, csv_file_name,
                    table_name=item.lower(),
                    table_schema=PG_SCHEMA,
                    primary_key='id',
                    csv_options={'HEADER': 'true'},
                    update_action="UPDATE")
        logging.info("Completed copying records to {} table.".format(item))
    os.remove(csv_file_name)


def db_write(job, item):
    if job.payload['zuora_state'] != 'completed':
        return

    http_response = job.payload['http_response']

    # TODO: process multiple batch
    batch = http_response['batches'][0]

    if batch['status'] != 'completed':
        return

    if batch.get('recordCount', 0) == 0:
        return

    db_write_incremental(item)


def zuora_query_params(item):
    query = "Select " + ', '.join(getZuoraFields(item)) + " FROM " + item
    # TODO: add Partner ID + Project ID to have incremental
    data = json.dumps({
        "format": "csv",
        "version": "1.2",
        "name": item_elt_uri(item),
        "encrypted": "none",
        "useQueryLabels": "true",
        "partner": environment['partner_id'],
        "project": environment['project_id'],
        "incrementalTime": item_incremental_time(item),
        "queries": [
            {
                "name": item,
                "query": query,
                "type": "zoqlexport",
                "apiVersion": "88.0"
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    return (headers, data)


def import_job(job, item):
    """
    Job pipeline:
      - Create an extract job
      - Wait for the extract job to be completed
      - Download the extracted file
      - Write it in the database

    Any exception caught here will change the job's state to `FAIL`
    set the `exception` key to the exception message.
    """
    try:
        job.transit(State.RUNNING)
        Job.save(job)

        create_extract_job(job, item)
        load_extract_job(job, job.payload['id'])
        filename = download_file(item, job.payload['file_id'])
        db_write(job, item)

        job.transit(State.SUCCESS)
    except DownloadError as download_err:
        job.payload['exception'] = str(err)

        next_state = State.DEAD if download_err.fatal else State.FAIL
        job.transit(next_state)
    except (Error, psycopg2.Error) as err:
        job.payload['exception'] = str(err)
        job.transit(State.FAIL)

        logging.error('Something went wrong: {}'.format(err))
    finally:
        job.ended_at = datetime.datetime.utcnow()

    Job.save(job)


def main():
    start = time.time()

    for item in getObjectList():
        for job in item_jobs(item):
            import_job(job, item)

    end = time.time()

    totalMinutes = (end - start) / 60
    logging.info('Completed Load in %1.1f minutes' % totalMinutes)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

    setup_db()

    with DB.open() as db:
        schema_apply(db, Job.describe_schema())
        schema_apply(db, describe_schema())

    main()
