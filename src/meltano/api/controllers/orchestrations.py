import logging

from flask import Blueprint, request, url_for, jsonify, make_response, Response

from meltano.core.job import JobFinder, State
from meltano.core.plugin import PluginRef
from meltano.core.plugin.error import PluginExecutionError
from meltano.core.plugin.settings_service import (
    PluginSettingsService,
    PluginSettingValueSource,
)
from meltano.core.plugin_discovery_service import PluginDiscoveryService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.config_service import ConfigService
from meltano.core.schedule_service import ScheduleService, ScheduleAlreadyExistsError
from meltano.core.select_service import SelectService
from meltano.core.tracking import GoogleAnalyticsTracker
from meltano.core.utils import flatten, iso8601_datetime, slugify
from meltano.cli.add import extractor
from meltano.api.models import db
from meltano.api.json import freeze_keys

from meltano.api.executor import run_elt


orchestrationsBP = Blueprint(
    "orchestrations", __name__, url_prefix="/api/v1/orchestrations"
)


@orchestrationsBP.route("/connection_names", methods=["GET"])
def connection_names():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
    connections = [
        c["name"] for c in settings.serializable()["settings"]["connections"]
    ]
    return jsonify(connections)


@orchestrationsBP.route("/job/state", methods=["POST"])
def job_state() -> Response:
    """
    endpoint for getting the status of N jobs
    """
    project = Project.find()
    poll_payload = request.get_json()
    job_ids = poll_payload["job_ids"]

    jobs = []
    for job_id in job_ids:
        finder = JobFinder(job_id)
        state_job = finder.latest(db.session)
        is_complete = state_job.state == State.SUCCESS
        jobs.append({"job_id": job_id, "is_complete": is_complete})

    return jsonify({"jobs": jobs})


@orchestrationsBP.route("/run", methods=["POST"])
def run():
    project = Project.find()
    schedule_payload = request.get_json()
    job_id = run_elt(project, schedule_payload)

    return jsonify({"job_id": job_id}), 202


@orchestrationsBP.route("/get/configuration", methods=["POST"])
def get_plugin_configuration() -> Response:
    """
    endpoint for getting a plugin's configuration
    """
    project = Project.find()
    payload = request.get_json()
    plugin = PluginRef(payload["type"], payload["name"])
    settings = PluginSettingsService(db.session, project)

    config = flatten(
        settings.as_config(plugin, sources=[PluginSettingValueSource.DB]), reducer="dot"
    )

    return jsonify(
        {
            "config": freeze_keys(config),
            "settings": settings.get_definition(plugin).settings,
        }
    )


@orchestrationsBP.route("/save/configuration", methods=["POST"])
def save_plugin_configuration() -> Response:
    """
    endpoint for persisting a plugin configuration
    """
    project = Project.find()
    incoming = request.get_json()
    plugin = PluginRef(incoming["type"], incoming["name"])
    config = incoming["config"]

    settings = PluginSettingsService(db.session, project)
    for name, value in config.items():
        if value == "":
            settings.unset(plugin, name)
        else:
            settings.set(plugin, name, value)

    return jsonify(settings.as_config(plugin))


@orchestrationsBP.route("/select-entities", methods=["POST"])
def selectEntities() -> Response:
    """
    endpoint that performs selection of the user selected entities and attributes
    """
    project = Project.find()
    incoming = request.get_json()
    extractor_name = incoming["extractor_name"]
    entity_groups = incoming["entity_groups"]
    select_service = SelectService(project, extractor_name)

    for entity_group in entity_groups:
        group_is_selected = "selected" in entity_group

        for attribute in entity_group["attributes"]:
            if group_is_selected or "selected" in attribute:
                entities_filter = entity_group["name"]
                attributes_filter = attribute["name"]
                select_service.select(entities_filter, attributes_filter)

    return jsonify("winning")


@orchestrationsBP.route("/entities/<extractor_name>", methods=["POST"])
def entities(extractor_name: str) -> Response:
    """
    endpoint that returns the entities associated with a particular extractor
    """
    project = Project.find()
    select_service = SelectService(project, extractor_name)

    entity_groups = []
    try:
        list_all = select_service.get_extractor_entities()

        for stream, prop in (
            (stream, prop)
            for stream in list_all.streams
            for prop in list_all.properties[stream.key]
        ):
            match = next(
                (
                    entityGroup
                    for entityGroup in entity_groups
                    if entityGroup["name"] == stream.key
                ),
                None,
            )
            if match:
                match["attributes"].append({"name": prop.key})
            else:
                entity_groups.append(
                    {"name": stream.key, "attributes": [{"name": prop.key}]}
                )

        entity_groups = sorted(entity_groups, key=lambda k: k["name"])
        for entityGroup in entity_groups:
            entityGroup["attributes"] = sorted(
                entityGroup["attributes"], key=lambda k: k["name"]
            )
    except PluginExecutionError as e:
        logging.warning(str(e))

    return jsonify({"extractor_name": extractor_name, "entity_groups": entity_groups})


@orchestrationsBP.route("/get/pipeline_schedules", methods=["GET"])
def get_pipeline_schedules():
    """
    endpoint for getting the pipeline schedules
    """
    project = Project.find()
    schedule_service = ScheduleService(db.session, project)
    schedules = [s._asdict() for s in schedule_service.schedules()]
    for schedule in schedules:
        finder = JobFinder(f"job_{schedule['name']}")
        state_job = finder.latest(db.session)
        is_running = state_job.state is State.RUNNING if state_job else False
        schedule["is_running"] = is_running

    return jsonify(schedules)


@orchestrationsBP.route("/save/pipeline_schedule", methods=["POST"])
def save_pipeline_schedule() -> Response:
    """
    endpoint for persisting a pipeline schedule
    """
    incoming = request.get_json()
    # Airflow requires alphanumeric characters, dashes, dots and underscores exclusively
    name = slugify(incoming["name"])
    extractor = incoming["extractor"]
    loader = incoming["loader"]
    transform = incoming["transform"]
    interval = incoming["interval"]
    start_date = incoming["start_date"]

    project = Project.find()
    schedule_service = ScheduleService(db.session, project)

    try:
        schedule = schedule_service.add(
            name,
            extractor,
            loader,
            transform,
            interval,
            start_date=iso8601_datetime(start_date),
        )
        return jsonify(schedule._asdict()), 201
    except ScheduleAlreadyExistsError as e:
        return jsonify(e.schedule), 200
