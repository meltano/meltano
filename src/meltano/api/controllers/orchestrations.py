import asyncio
import json
import logging
import shutil

import sqlalchemy
from flask import Response, jsonify, make_response, request, send_file, url_for
from flask_restful import Api, Resource, fields, marshal, marshal_with
from flask_security import roles_required
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.executor import run_schedule
from meltano.api.json import freeze_keys
from meltano.api.models import db
from meltano.api.models.subscription import Subscription
from meltano.api.security.auth import block_if_readonly
from meltano.core.behavior.canonical import Canonical
from meltano.core.job import JobFinder, State
from meltano.core.logging import (
    JobLoggingService,
    MissingJobLogException,
    SizeThresholdJobLogException,
)
from meltano.core.plugin import PluginRef
from meltano.core.plugin.error import PluginExecutionError, PluginLacksCapabilityError
from meltano.core.plugin.settings_service import (
    PluginSettingsService,
    SettingValueStore,
)
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.schedule_service import (
    ScheduleAlreadyExistsError,
    ScheduleDoesNotExistError,
    ScheduleService,
)
from meltano.core.setting_definition import SettingKind
from meltano.core.utils import flatten, iso8601_datetime, slugify
from werkzeug.exceptions import Conflict, UnprocessableEntity

from .errors import InvalidFileNameError
from .upload_helper import InvalidFileSizeError, InvalidFileTypeError, UploadHelper
from .utils import enforce_secure_filename


def get_config_with_metadata(settings):
    config_dict = {}
    config_metadata = {}

    config_with_metadata = settings.config_with_metadata(
        extras=False, redacted=True, session=db.session
    )
    for key, metadata in config_with_metadata.items():
        config_dict[key] = metadata.pop("value")

        metadata.pop("setting", None)

        try:
            metadata["source_label"] = metadata["source"].label
            metadata["auto_store_label"] = metadata["auto_store"].label
        except KeyError:
            pass

        config_metadata[key] = metadata

    return {
        "config": freeze_keys(config_dict),
        "config_metadata": freeze_keys(config_metadata),
    }


def validate_plugin_config(
    plugin: PluginRef, name, value, project: Project, settings: PluginSettingsService
):
    setting_def = settings.find_setting(name)
    # we want to prevent the edition of protected settings from the UI
    if setting_def.protected:
        logging.warning("Cannot set a 'protected' setting externally.")
        return False

    if setting_def.kind == SettingKind.FILE and value and value != "":
        uploads_directory = project.extract_dir(plugin.name)
        resolved_file_path = project.root_dir(value).resolve()
        if not str(resolved_file_path).startswith(str(uploads_directory) + "/"):
            logging.warning(
                "Cannot set a file configuration to a path outside the project directory"
            )
            return False

    old_value, metadata = settings.get_with_metadata(name, session=db.session)
    if not metadata["overwritable"]:
        logging.warning("Cannot overwrite this setting.")
        return False

    return True


orchestrationsBP = APIBlueprint("orchestrations", __name__)
orchestrationsAPI = Api(
    orchestrationsBP,
    errors={
        "UnprocessableEntity": {
            "error": True,
            "code": "The subscription could not be created.",
            "status": UnprocessableEntity.code,
        },
        "Conflict": {
            "error": True,
            "code": "A subscription already exists for this address.",
            "status": Conflict.code,
        },
    },
)


@orchestrationsBP.errorhandler(ScheduleAlreadyExistsError)
def _handle(ex):  # noqa: F811
    return (
        jsonify(
            {
                "error": True,
                "code": f"A pipeline with the name '{ex.schedule.name}' already exists. Try renaming the pipeline.",
            }
        ),
        409,
    )


@orchestrationsBP.errorhandler(ScheduleDoesNotExistError)
def _handle(ex):  # noqa: F811
    return (
        jsonify(
            {
                "error": True,
                "code": f"A pipeline with the name '{ex.name}' does not exist..",
            }
        ),
        404,
    )


@orchestrationsBP.errorhandler(InvalidFileNameError)
def _handle(ex):  # noqa: F811
    return (jsonify({"error": True, "code": f"The file lacks a valid name."}), 400)


@orchestrationsBP.errorhandler(InvalidFileTypeError)
def _handle(ex):  # noqa: F811
    return (
        jsonify(
            {
                "error": True,
                "code": f"The file '{ex.file.filename}' must be one of the following types: {ex.extensions}",
            }
        ),
        400,
    )


@orchestrationsBP.errorhandler(InvalidFileSizeError)
def _handle(ex):  # noqa: F811
    return (
        jsonify(
            {
                "error": True,
                "code": f"The file '{ex.file.filename}' is empty or exceeds the {ex.max_file_size} size limit.",
            }
        ),
        400,
    )


@orchestrationsBP.errorhandler(MissingJobLogException)
def _handle(ex):  # noqa: F811
    return (jsonify({"error": False, "code": str(ex)}), 204)


@orchestrationsBP.route("/jobs/state", methods=["POST"])
def job_state() -> Response:
    """
    Endpoint for getting the status of N jobs
    """
    project = Project.find()
    poll_payload = request.get_json()
    job_ids = poll_payload["job_ids"]

    jobs = []
    for job_id in job_ids:
        finder = JobFinder(job_id)
        state_job = finder.latest(db.session)
        # Validate existence first as a job may not be queued yet as a result of
        # another prerequisite async process (dbt installation for example)
        if state_job:
            state_job_success = finder.latest_success(db.session)
            jobs.append(
                {
                    "job_id": job_id,
                    "is_complete": state_job.is_complete(),
                    "has_error": state_job.has_error(),
                    "started_at": state_job.started_at,
                    "ended_at": state_job.ended_at,
                    "has_ever_succeeded": state_job_success.is_success()
                    if state_job_success
                    else None,
                }
            )

    return jsonify({"jobs": jobs})


@orchestrationsBP.route("/jobs/<job_id>/log", methods=["GET"])
def job_log(job_id) -> Response:
    """
    Endpoint for getting the most recent log generated by a job with job_id
    """
    project = Project.find()
    try:
        log_service = JobLoggingService(project)
        log = log_service.get_latest_log(job_id)
        has_log_exceeded_max_size = False
    except SizeThresholdJobLogException as err:
        log = None
        has_log_exceeded_max_size = True

    finder = JobFinder(job_id)
    state_job = finder.latest(db.session)
    state_job_success = finder.latest_success(db.session)

    return jsonify(
        {
            "job_id": job_id,
            "log": log,
            "has_log_exceeded_max_size": has_log_exceeded_max_size,
            "has_error": state_job.has_error() if state_job else False,
            "started_at": state_job.started_at if state_job else None,
            "ended_at": state_job.ended_at if state_job else None,
            "trigger": state_job.trigger if state_job else None,
            "has_ever_succeeded": state_job_success.is_success()
            if state_job_success
            else None,
        }
    )


@orchestrationsBP.route("/jobs/<job_id>/download", methods=["GET"])
def download_job_log(job_id) -> Response:
    """
    Endpoint for downloading a job log with job_id
    """
    project = Project.find()
    log_service = JobLoggingService(project)
    return send_file(log_service.get_downloadable_log(job_id), mimetype="text/plain")


@orchestrationsBP.route("/run", methods=["POST"])
def run():
    project = Project.find()
    schedule_payload = request.get_json()
    name = schedule_payload["name"]
    job_id = run_schedule(project, name)

    return jsonify({"job_id": job_id}), 202


@orchestrationsBP.route(
    "/<plugin_ref:plugin_ref>/configuration/upload-file", methods=["POST"]
)
@block_if_readonly
def upload_plugin_configuration_file(plugin_ref) -> Response:
    """
    Endpoint for uploading a file for a specific plugin
    """

    file = request.files["file"]
    setting_name = enforce_secure_filename(request.form["setting_name"])
    tmp = request.form.get("tmp", False)

    project = Project.find()
    directory = project.extract_dir(
        plugin_ref.name, ("tmp" if tmp else ""), setting_name
    )
    upload_helper = UploadHelper()
    file_path = upload_helper.upload_file(directory, file)

    return jsonify({"path": file_path, "setting_name": setting_name}), 200


@orchestrationsBP.route(
    "/<plugin_ref:plugin_ref>/configuration/delete-uploaded-file", methods=["POST"]
)
@block_if_readonly
def delete_plugin_configuration_file(plugin_ref) -> Response:
    """
    Endpoint for deleting a file for a specific plugin
    """

    payload = request.get_json()
    setting_name = enforce_secure_filename(payload["setting_name"])
    tmp = payload.get("tmp", False)

    project = Project.find()
    directory = project.extract_dir(
        plugin_ref.name, ("tmp" if tmp else ""), setting_name
    )
    shutil.rmtree(directory)

    return jsonify({"setting_name": setting_name}), 200


@orchestrationsBP.route("/<plugin_ref:plugin_ref>/configuration", methods=["GET"])
def get_plugin_configuration(plugin_ref) -> Response:
    """
    Endpoint for getting a plugin's configuration
    """

    project = Project.find()

    plugins_service = ProjectPluginsService(project)
    plugin = plugins_service.get_plugin(plugin_ref)

    settings = PluginSettingsService(
        project, plugin, plugins_service=plugins_service, show_hidden=False
    )

    try:
        settings_group_validation = plugin.settings_group_validation
    except PluginNotFoundError:
        settings_group_validation = []

    return jsonify(
        {
            **get_config_with_metadata(settings),
            "settings": Canonical.as_canonical(settings.definitions(extras=False)),
            "settings_group_validation": settings_group_validation,
        }
    )


@orchestrationsBP.route("/<plugin_ref:plugin_ref>/configuration", methods=["PUT"])
@block_if_readonly
def save_plugin_configuration(plugin_ref) -> Response:
    """
    Endpoint for persisting a plugin configuration
    """
    project = Project.find()
    payload = request.get_json()
    plugins_service = ProjectPluginsService(project)
    plugin = plugins_service.get_plugin(plugin_ref)

    settings = PluginSettingsService(
        project, plugin, plugins_service=plugins_service, show_hidden=False
    )

    config = payload.get("config", {})
    for name, value in config.items():
        if not validate_plugin_config(plugin, name, value, project, settings):
            continue

        if value == "":
            settings.unset(name, session=db.session)
        else:
            settings.set(name, value, session=db.session)

    return jsonify(get_config_with_metadata(settings))


@orchestrationsBP.route("/<plugin_ref:plugin_ref>/configuration/test", methods=["POST"])
@block_if_readonly
def test_plugin_configuration(plugin_ref) -> Response:
    """
    Endpoint for testing a plugin configuration's valid connection
    """
    project = Project.find()
    payload = request.get_json()
    plugins_service = ProjectPluginsService(project)
    plugin = plugins_service.get_plugin(plugin_ref)

    settings = PluginSettingsService(
        project, plugin, plugins_service=plugins_service, show_hidden=False
    )

    config = payload.get("config", {})
    valid_config = {
        name: value
        for name, value in config.items()
        if validate_plugin_config(plugin, name, value, project, settings)
    }
    settings.config_override = PluginSettingsService.unredact(valid_config)

    async def test_stream(tap_stream) -> bool:
        while not tap_stream.at_eof():
            message = await tap_stream.readline()
            json_dict = json.loads(message)
            if json_dict["type"] == "RECORD":
                return True

        return False

    async def test_extractor():
        process = None
        try:
            invoker = invoker_factory(
                project,
                plugin,
                plugins_service=plugins_service,
                plugin_settings_service=settings,
            )
            with invoker.prepared(db.session):
                process = await invoker.invoke_async(stdout=asyncio.subprocess.PIPE)
                return await test_stream(process.stdout)
        except Exception as err:
            logging.debug(err)
            # if anything happens, this is not successful
            return False
        finally:
            try:
                if process:
                    psutil.Process(process.pid).terminate()
            except Exception as err:
                logging.debug(err)

    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_extractor())

    return jsonify({"is_success": success}), 200


@orchestrationsBP.route("/pipeline-schedules", methods=["GET"])
def get_pipeline_schedules():
    """
    Endpoint for getting the pipeline schedules
    """
    project = Project.find()
    schedule_service = ScheduleService(project)
    schedules = list(map(dict, schedule_service.schedules()))
    for schedule in schedules:
        finder = JobFinder(schedule["name"])
        state_job = finder.latest(db.session)
        schedule["has_error"] = state_job.has_error() if state_job else False
        schedule["is_running"] = state_job.is_running() if state_job else False
        schedule["job_id"] = schedule["name"]
        schedule["started_at"] = state_job.started_at if state_job else None
        schedule["ended_at"] = state_job.ended_at if state_job else None
        schedule["trigger"] = state_job.trigger if state_job else None

        state_job_success = finder.latest_success(db.session)
        schedule["has_ever_succeeded"] = (
            state_job_success.is_success() if state_job_success else None
        )

        schedule["start_date"] = (
            schedule["start_date"].date().isoformat()
            if schedule["start_date"]
            else None
        )

    return jsonify(schedules)


@orchestrationsBP.route("/pipeline-schedules", methods=["POST"])
@block_if_readonly
def save_pipeline_schedule() -> Response:
    """
    Endpoint for persisting a pipeline schedule
    """
    payload = request.get_json()
    # Airflow requires alphanumeric characters, dashes, dots and underscores exclusively
    name = payload["name"]
    slug = slugify(name)
    extractor = payload["extractor"]
    loader = payload["loader"]
    transform = payload["transform"]
    interval = payload["interval"]

    project = Project.find()
    schedule_service = ScheduleService(project)

    schedule = schedule_service.add(
        db.session, slug, extractor, loader, transform, interval
    )

    schedule = dict(schedule)
    schedule["start_date"] = (
        schedule["start_date"].date().isoformat() if schedule["start_date"] else None
    )

    return jsonify(schedule), 201


@orchestrationsBP.route("/pipeline-schedules", methods=["PUT"])
@block_if_readonly
def update_pipeline_schedule() -> Response:
    """
    Endpoint for updating a pipeline schedule
    """
    payload = request.get_json()
    project = Project.find()
    schedule_service = ScheduleService(project)

    interval = payload["interval"]
    plugin_namespace = payload["plugin_namespace"]
    schedule = schedule_service.find_namespace_schedule(plugin_namespace)
    schedule.interval = interval
    schedule_service.update_schedule(schedule)

    schedule = dict(schedule)
    schedule["start_date"] = (
        schedule["start_date"].date().isoformat() if schedule["start_date"] else None
    )

    return jsonify(schedule), 201


@orchestrationsBP.route("/pipeline-schedules", methods=["DELETE"])
@block_if_readonly
def delete_pipeline_schedule() -> Response:
    """
    Endpoint for deleting a pipeline schedule
    """
    payload = request.get_json()
    project = Project.find()
    schedule_service = ScheduleService(project)

    name = payload["name"]
    schedule_service.remove(name)
    return jsonify(name), 201


class SubscriptionsResource(Resource):
    SubscriptionDefinition = {
        "id": fields.String,
        "recipient": fields.String,
        "event_type": fields.String,
        "source_type": fields.String,
        "source_id": fields.String,
        "created_at": fields.DateTime,
    }

    @marshal_with(SubscriptionDefinition)
    def get(self):
        return Subscription.query.all()

    @marshal_with(SubscriptionDefinition)
    def post(self):
        payload = request.get_json()

        try:
            subscription = Subscription(**payload)
            db.session.add(subscription)
            db.session.commit()
        except AssertionError as err:
            raise UnprocessableEntity() from err
        except sqlalchemy.exc.IntegrityError:
            raise Conflict()

        return subscription, 201


class SubscriptionResource(Resource):
    def delete(self, id):
        Subscription.query.filter_by(id=id).delete()
        db.session.commit()

        return "", 204


orchestrationsAPI.add_resource(SubscriptionsResource, "/subscriptions")
orchestrationsAPI.add_resource(SubscriptionResource, "/subscriptions/<id>")
