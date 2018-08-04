import time
import json
import csv
import re
import os
import datetime
import requests
import logging
import psycopg2
import psycopg2.sql

from elt.error import ExtractError
from elt.db import db_open
from elt.cli import ExportOutput, DateWindow
from elt.process import upsert_to_db_from_csv
from .mkto_token import get_token, mk_endpoint
from .mkto_leads import get_leads_fieldnames_mkto, describe_leads
from .mkto_utils import bulk_filter_builder, get_mkto_config, handle_marketo_response
from config import MarketoSource, ExportType, config_table_name, config_primary_key


FIELD_CREATED_AT = "createdAt"
FIELD_UPDATED_AT = "updatedAt"


def auth_headers(token, content_type="application/json"):
    return {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": content_type,
    }


def bulk_create_job(filter, data_type, fields=None, format="CSV", column_header_names=None):
    """
    Create a bulk job
    :param filter: dictionary of filtering parameters (createdAt, fields, activityIds, etc)
    :param data_type: "leads" or "activities"
    :param fields: Optional list of fields to filter by
    :param format: returns CSV file by default, other options are TSV and SSV
    :param column_header_names: optional dictionary of preferred column header names i.e. => {
          "firstName": "First Name",
          "email": "Email Address"
       }
    :return: json data
    """
    token = get_token()
    create_url = "{}bulk/v1/{}/export/create.json".format(mk_endpoint, data_type)

    payload = {
        "format": format,
        "filter": filter,
    }

    if fields is not None:
        payload["fields"] = fields

    if column_header_names is not None:
        payload["columnHeaderNames"] = column_header_names

    response = requests.post(create_url,
                             json=payload,
                             headers=auth_headers(token))

    return handle_marketo_response(response)


def bulk_get_export_jobs(data_type, status=None, batch_size=10):
    """
    Get a list of previous jobs
    :param data_type: "leads" or "activities"
    :param status: Optional filter by status
    :param batch_size: returns 10 jobs by default
    :return: json data
    """

    export_url = "{}bulk/v1/{}/export.json".format(mk_endpoint, data_type)
    payload = {
        "access_token": get_token(),
        "batchSize": batch_size,
    }

    if status is not None:
        payload["status"] = ','.join(status)

    response = requests.get(export_url, params=payload)
    return handle_marketo_response(response)


def bulk_enqueue_job(data_type, export_id):
    """
    Enqueue a created job
    :param data_type: "leads" or "activites"
    :param export_id: guid
    :return: json data
    """
    token = get_token()
    enqueue_url = "{}bulk/v1/{}/export/{}/enqueue.json".format(mk_endpoint, data_type, export_id)

    response = requests.post(enqueue_url, headers=auth_headers(token))
    return handle_marketo_response(response)


def bulk_job_status(data_type, export_id):
    """
    Query for the status of a bulk job
    :param data_type: "leads" or "activities"
    :param export_id: guid
    :return: json data
    """

    token = get_token()
    status_url = "{}bulk/v1/{}/export/{}/status.json".format(mk_endpoint, data_type, export_id)

    payload = {
        "access_token": token,
    }

    response = requests.get(status_url, params=payload)
    return handle_marketo_response(response)


def bulk_get_file(data_type, export_id):
    """
    Download the CSV of a completed job. Can be called while job is still processsing.
    :param data_type: "leads" or "activities"
    :param export_id: guid
    :return:
    """
    file_url = "{}bulk/v1/{}/export/{}/file.json".format(mk_endpoint, data_type, export_id)
    output_file = "{}.csv".format(data_type)

    while True:
        status_result = bulk_job_status(data_type, export_id)
        job_status = status_result.get("result", [])[0].get("status")
        if job_status == "Completed":
            break
        elif job_status == "Failed":
            logging.info("Job Failed")
            return
        else:
            logging.info("Job Status is " + job_status)
            logging.info("Waiting for 60 seconds.")
            time.sleep(60)
            continue

    logging.info("File {} available at {}".format(output_file, file_url))

    with requests.Session() as s:
        payload = {
            "access_token": get_token(),
        }
        download = s.get(file_url, params=payload)

        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')

    with open(file=output_file, mode='w', newline='') as csvfile:
        logging.info("Writing file...")
        csvwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in cr:
            csvwriter.writerow(row)
        logging.info("File written at {}.".format(output_file))



def bulk_cancel_job(data_type, export_id):
    """
    Cancel a currently running job.

    :param data_type: "leads" or "activities"
    :param export_id: guid
    :return:
    """

    token = get_token()
    cancel_url = "{}bulk/v1/{}/export/{}/cancel.json".format(mk_endpoint, data_type, export_id)

    response = requests.post(cancel_url, headers=auth_headers(token))

    return handle_marketo_response(response)


def bulk_export(args):
    fields = None
    activity_ids = None
    output_file = "{}.csv".format(args.source)

    try:
        window = DateWindow(args, formatter=lambda t: t.isoformat() + 'Z')
        (date_start, date_end) = window.formatted_range()
    except TypeError as e:
        raise ExtractError("Start/End date is not in the proper format: {}".format(e))

    if args.type == ExportType.CREATED:
        pull_type = FIELD_CREATED_AT

    if args.type == ExportType.UPDATED:
        pull_type = FIELD_UPDATED_AT

    if args.source == MarketoSource.ACTIVITIES:
        # If Activities, default is to get all activity types. All fields are returned by Marketo API by default
        activity_objects = get_mkto_config('Activities', 'objects')
        activity_ids = [int(get_mkto_config(ob, 'id')) for ob in activity_objects.split(',')]

    if args.source == MarketoSource.LEADS:
        # This is an API call to Marketo. Should probably pull from static config and periodically check for differences
        fields = get_leads_fieldnames_mkto(describe_leads())

    filter = bulk_filter_builder(start_date=date_start,
                                 end_date=date_end,
                                 pull_type=pull_type,
                                 activity_ids=activity_ids)
    new_job = bulk_create_job(filter=filter, data_type=args.source, fields=fields)
    logging.debug(json.dumps(new_job, indent=2))

    export_id = new_job.get("result", ["None"])[0].get("exportId")
    logging.info("Enqueuing Job")
    bulk_enqueue_job(args.source, export_id)

    logging.info("Get Results File")
    bulk_get_file(args.source, export_id)

    if args.output == ExportOutput.DB:
        options = config_integrate(args)

        logging.info("Upserting to Database")
        with db_open() as db:
            upsert_to_db_from_csv(db, output_file, **options)

    if args.nodelete or args.output == ExportOutput.FILE:
        return
    else:
        os.remove(output_file)
