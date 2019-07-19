import asyncio
import datetime
import logging
import os

from flask import Blueprint, request, url_for, jsonify, make_response, Response, g

from meltano.core.plugin import PluginRef, PluginType
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
from meltano.core.utils import flatten, iso8601_datetime
from meltano.api.models import db
from meltano.api.workers import ELTWorker
from meltano.cli.add import extractor

from meltano.core.runner.dbt import DbtRunner
from meltano.core.runner.singer import SingerRunner


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


def runElt(project: Project, schedule_payload: dict):
    extractor = schedule_payload["extractor"]
    loader = schedule_payload["loader"]
    transform = schedule_payload.get("transform")
    schedule_name = schedule_payload.get("name")
    job_id = f'job_{schedule_name}_{datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S.%f")}'

    singer_runner = SingerRunner(
        project,
        job_id=job_id,
        run_dir=os.getenv("SINGER_RUN_DIR", project.meltano_dir("run")),
        target_config_dir=project.meltano_dir(PluginType.LOADERS, loader),
        tap_config_dir=project.meltano_dir(
            PluginType.EXTRACTORS, extractor
        ),
    )

    try:
        if transform == "run" or transform == "skip":
            print("run *************")
            singer_runner.run(extractor, loader)
        if transform == "run":
            dbt_runner = DbtRunner(project)
            dbt_runner.run(extractor, loader, models=extractor)
    except Exception as err:
        raise Exception(
            "ELT could not complete, an error happened during the process."
        )


@orchestrationsBP.route("/run", methods=["POST"])
def run():
    project = Project.find()
    schedule_payload = request.get_json()
    future = g.executor.submit(runElt, project, schedule_payload)

    return jsonify({"test": "winning"})


@orchestrationsBP.route("/get/configuration", methods=["POST"])
def get_plugin_configuration() -> Response:
    """
    endpoint for getting a plugin's configuration
    """
    project = Project.find()
    payload = request.get_json()
    plugin = PluginRef(payload["type"], payload["name"])
    settings = PluginSettingsService(db.session, project)

    return jsonify(
        {
            "config": flatten(
                settings.as_config(plugin, sources=[PluginSettingValueSource.DB]),
                reducer="dot",
            ),
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
    extractor_name = incoming["extractorName"]
    entity_groups = incoming["entityGroups"]
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
    schedules = schedule_service.schedules()

    cleaned_schedules = []
    for schedule in list(schedules):
        cleaned_schedules.append(
            {
                "name": schedule.name,
                "extractor": schedule.extractor,
                "loader": schedule.loader,
                "transform": schedule.transform,
                "interval": schedule.interval,
                "startDate": schedule.start_date,
            }
        )

    return jsonify(cleaned_schedules)


@orchestrationsBP.route("/save/pipeline_schedule", methods=["POST"])
def save_pipeline_schedule() -> Response:
    """
    endpoint for persisting a pipeline schedule
    """
    incoming = request.get_json()
    name = incoming["name"]
    extractor = incoming["extractor"]
    loader = incoming["loader"]
    transform = incoming["transform"]
    interval = incoming["interval"]
    start_date = incoming["startDate"]

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
        return jsonify(schedule), 201
    except ScheduleAlreadyExistsError as e:
        return jsonify(e.schedule), 200
