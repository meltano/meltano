"""API Orchestation of Pipellines and Validations."""

from __future__ import annotations

import asyncio
import logging
import shutil

import sqlalchemy
from flask import Response, jsonify, request, send_file
from flask_restful import Api, Resource, fields, marshal_with
from werkzeug.exceptions import Conflict, UnprocessableEntity

from meltano.api.api_blueprint import APIBlueprint
from meltano.api.executor import run_schedule
from meltano.api.json import freeze_keys
from meltano.api.models import db
from meltano.api.models.subscription import Subscription
from meltano.api.security.auth import block_if_readonly
from meltano.core.behavior.canonical import Canonical
from meltano.core.job import JobFinder
from meltano.core.logging import (
    JobLoggingService,
    MissingJobLogException,
    SizeThresholdJobLogException,
)
from meltano.core.plugin import PluginRef
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_discovery_service import PluginNotFoundError
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.plugin_test_service import PluginTestServiceFactory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.schedule_service import (
    ScheduleAlreadyExistsError,
    ScheduleDoesNotExistError,
    ScheduleService,
)
from meltano.core.setting_definition import SettingKind
from meltano.core.settings_service import FeatureFlags
from meltano.core.utils import slugify

from .errors import InvalidFileNameError
from .upload_helper import InvalidFileSizeError, InvalidFileTypeError, UploadHelper
from .utils import enforce_secure_filename


def get_config_with_metadata(settings):
    """Get configuration including metadata.

    Args:
        settings: List of settings to obtain metadata for.

    Returns:
        Configuration with setting metadata
    """
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
    """Check the plugin configuration.

    Args:
        plugin: PluginRef class.
        name: Name of the plugin to validate
        value: Name of plugin setting file
        project: Project class.
        settings: PluginSettingsService class.

    Returns:
        A boolean true for pass, false for fail.
    """
    setting_def = settings.find_setting(name)
    # we want to prevent the edition of protected settings from the UI
    if setting_def.protected:
        logging.warning("Cannot set a 'protected' setting externally.")
        return False

    if setting_def.kind == SettingKind.FILE and value and value != "":
        uploads_directory = project.extract_dir(plugin.name)
        resolved_file_path = project.root_dir(value).resolve()
        if not str(resolved_file_path).startswith(f"{uploads_directory}/"):
            logging.warning(
                "Cannot set a file configuration to a path outside the project directory"
            )
            return False

    old_value, metadata = settings.get_with_metadata(name, session=db.session)
    if not metadata["overwritable"]:
        logging.warning("Cannot overwrite this setting.")
        return False

    return True


orchestrations_bp = APIBlueprint("orchestrations", __name__)  # noqa: N816
orchestrationsAPI = Api(  # noqa: N816
    orchestrations_bp,
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


@orchestrations_bp.errorhandler(ScheduleAlreadyExistsError)  # noqa: F811
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"A pipeline with the name '{ex.schedule.name}' already exists. Try renaming the pipeline.",
            }
        ),
        409,
    )


@orchestrations_bp.errorhandler(ScheduleDoesNotExistError)  # noqa: F811
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"A pipeline with the name '{ex.name}' does not exist..",
            }
        ),
        404,
    )


@orchestrations_bp.errorhandler(InvalidFileNameError)  # noqa: F811
def _handle(ex):
    return (jsonify({"error": True, "code": "The file lacks a valid name."}), 400)


@orchestrations_bp.errorhandler(InvalidFileTypeError)  # noqa: F811
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"The file '{ex.file.filename}' must be one of the following types: {ex.extensions}",
            }
        ),
        400,
    )


@orchestrations_bp.errorhandler(InvalidFileSizeError)  # noqa: F811
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"The file '{ex.file.filename}' is empty or exceeds the {ex.max_file_size} size limit.",
            }
        ),
        400,
    )


@orchestrations_bp.errorhandler(MissingJobLogException)  # noqa: F811
def _handle(ex):
    return (jsonify({"error": False, "code": str(ex)}), 204)


@orchestrations_bp.route("/jobs/state", methods=["POST"])
def job_state() -> Response:
    """Endpoint for getting the status of N jobs.

    Returns:
        A JSON containing all the endpoint job status for the N jobs.
    """
    poll_payload = request.get_json()
    state_ids = poll_payload["state_ids"]

    jobs = []
    for state_id in state_ids:
        finder = JobFinder(state_id)
        state_job = finder.latest(db.session)
        # Validate existence first as a job may not be queued yet as a result of
        # another prerequisite async process (dbt installation for example)
        if state_job:
            state_job_success = finder.latest_success(db.session)
            jobs.append(
                {
                    "state_id": state_id,
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


@orchestrations_bp.route("/jobs/<state_id>/log", methods=["GET"])
def job_log(state_id) -> Response:
    """Endpoint for getting the most recent log generated by a job with state_id.

    Args:
        state_id: id of the job you want to see logs of.

    Returns:
        JSON containing the jobs log entries
    """
    project = Project.find()
    try:
        log_service = JobLoggingService(project)
        log = log_service.get_latest_log(state_id)
        has_log_exceeded_max_size = False
    except SizeThresholdJobLogException:
        log = None
        has_log_exceeded_max_size = True

    finder = JobFinder(state_id)
    state_job = finder.latest(db.session)
    state_job_success = finder.latest_success(db.session)

    return jsonify(
        {
            "state_id": state_id,
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


@orchestrations_bp.route("/jobs/<state_id>/download", methods=["GET"])
def download_job_log(state_id) -> Response:
    """Endpoint for downloading a job log with state_id.

    Args:
        state_id: id of the job you want log info of.

    Returns:
        A plain text file of the job log.
    """
    project = Project.find()
    log_service = JobLoggingService(project)
    return send_file(log_service.get_downloadable_log(state_id), mimetype="text/plain")


@orchestrations_bp.route("/run", methods=["POST"])
def run():
    """Run all scheduled payloads.

    Returns:
        JSON of all the state_ids that just ran.
    """
    project = Project.find()
    schedule_payload = request.get_json()
    name = schedule_payload["name"]
    state_id = run_schedule(project, name)

    return jsonify({"state_id": state_id}), 202


@orchestrations_bp.route(
    "/<plugin_ref:plugin_ref>/configuration/upload-file", methods=["POST"]
)
@block_if_readonly
def upload_plugin_configuration_file(plugin_ref) -> Response:
    """Endpoint for uploading a file for a specific plugin.

    Args:
        plugin_ref: Plugin being referenced.

    Returns:
        JSON contain the file path and setting name.
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


@orchestrations_bp.route(
    "/<plugin_ref:plugin_ref>/configuration/delete-uploaded-file", methods=["POST"]
)
@block_if_readonly
def delete_plugin_configuration_file(plugin_ref) -> Response:
    """Endpoint for deleting a file for a specific plugin.

    Args:
        plugin_ref: Plugin being referenced.

    Returns:
        JSON contain the setting name.
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


@orchestrations_bp.route("/<plugin_ref:plugin_ref>/configuration", methods=["GET"])
def get_plugin_configuration(plugin_ref) -> Response:
    """Endpoint for getting a plugin's configuration.

    Args:
        plugin_ref: Plugin being referenced.

    Returns:
        JSON contain the plugin configuration.
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


@orchestrations_bp.route("/<plugin_ref:plugin_ref>/configuration", methods=["PUT"])
@block_if_readonly
def save_plugin_configuration(plugin_ref) -> Response:
    """Endpoint for persisting a plugin configuration.

    Args:
        plugin_ref: Plugin being referenced.

    Returns:
        JSON contain the saved configuration.
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


@orchestrations_bp.route(
    "/<plugin_ref:plugin_ref>/configuration/test", methods=["POST"]
)
@block_if_readonly
def test_plugin_configuration(plugin_ref) -> Response:  # noqa: WPS210
    """Endpoint for testing a plugin configuration's valid connection.

    Args:
        plugin_ref: Plugin being referenced.

    Returns:
        JSON with the job sucess status.
    """
    project = Project.find()
    plugins_service = ProjectPluginsService(project)
    plugin = plugins_service.get_plugin(plugin_ref)

    settings = PluginSettingsService(
        project, plugin, plugins_service=plugins_service, show_hidden=False
    )

    settings.config_override = PluginSettingsService.unredact(
        {
            name: value
            for name, value in request.get_json().get("config", {}).items()
            if validate_plugin_config(plugin, name, value, project, settings)
        }
    )

    async def test_extractor():
        invoker = invoker_factory(
            project,
            plugin,
            plugins_service=plugins_service,
            plugin_settings_service=settings,
        )
        async with invoker.prepared(db.session):
            plugin_test_service = PluginTestServiceFactory(invoker).get_test_service()
            success, _ = await plugin_test_service.validate()
            return success

    # This was added to assist api_worker threads
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logging.debug("../configuration/test no asyncio event loop detected")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return jsonify({"is_success": loop.run_until_complete(test_extractor())}), 200


@orchestrations_bp.route("/pipeline-schedules", methods=["GET"])
def get_pipeline_schedules():
    """Endpoint for getting the pipeline schedules.

    Note that unless the ff ENABLE_API_SCHEDULED_JOB_LIST is enabled this endpoint will filter out scheduled jobs.

    Returns:
        JSON containing the pipline schedules.
    """
    project = Project.find()
    schedule_service = ScheduleService(project)
    schedules = list(map(dict, schedule_service.schedules()))

    jobs_in_list = False
    with ProjectSettingsService(project).feature_flag(
        FeatureFlags.ENABLE_API_SCHEDULED_JOB_LIST, raise_error=False
    ) as allow:
        if allow:
            jobs_in_list = True

    formatted_schedules = []

    for schedule in schedules:
        if schedule.get("job") and jobs_in_list:
            # we only return API results for scheduled jobs if the feature flag is explicitly enabled
            # as the UI is not job aware yet.
            formatted_schedules.append(schedule)
        elif not schedule.get("job"):  # a legacy elt task
            finder = JobFinder(schedule["name"])
            state_job = finder.latest(db.session)
            schedule["has_error"] = state_job.has_error() if state_job else False
            schedule["is_running"] = state_job.is_running() if state_job else False
            schedule["state_id"] = schedule["name"]
            schedule["started_at"] = state_job.started_at if state_job else None
            schedule["ended_at"] = state_job.ended_at if state_job else None
            schedule["trigger"] = state_job.trigger if state_job else None

            state_job_success = finder.latest_success(db.session)
            schedule["has_ever_succeeded"] = (
                state_job_success.is_success() if state_job_success else None
            )

            schedule["start_date"] = (  # noqa: WPS204
                schedule["start_date"].date().isoformat()
                if schedule["start_date"]
                else None
            )
            formatted_schedules.append(schedule)

    return jsonify(formatted_schedules)


@orchestrations_bp.route("/pipeline-schedules", methods=["POST"])
@block_if_readonly
def save_pipeline_schedule() -> Response:
    """Endpoint for persisting a pipeline schedule.

    Returns:
        JSON containing the saved pipline scheudles and status.
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

    schedule = schedule_service.add_elt(
        db.session, slug, extractor, loader, transform, interval
    )

    schedule = dict(schedule)
    schedule["start_date"] = (
        schedule["start_date"].date().isoformat() if schedule["start_date"] else None
    )

    return jsonify(schedule), 201


@orchestrations_bp.route("/pipeline-schedules", methods=["PUT"])
@block_if_readonly
def update_pipeline_schedule() -> Response:
    """Endpoint for updating a pipeline schedule.

    Returns:
        JSON containing the updated pipeline schedules and status.
    """
    payload = request.get_json()
    project = Project.find()
    schedule_service = ScheduleService(project)

    plugin_namespace = payload["plugin_namespace"]
    schedule = schedule_service.find_namespace_schedule(plugin_namespace)

    if "interval" in payload:
        schedule.interval = payload.get("interval")

    if "transform" in payload:
        schedule.transform = payload.get("transform")

    schedule_service.update_schedule(schedule)

    schedule = dict(schedule)
    schedule["start_date"] = (
        schedule["start_date"].date().isoformat() if schedule["start_date"] else None
    )

    return jsonify(schedule), 201


@orchestrations_bp.route("/pipeline-schedules", methods=["DELETE"])
@block_if_readonly
def delete_pipeline_schedule() -> Response:
    """Endpoint for deleting a pipeline schedule.

    Returns:
        JSON containing the deleted pipelinea and status.
    """
    payload = request.get_json()
    project = Project.find()
    schedule_service = ScheduleService(project)

    name = payload["name"]
    schedule_service.remove(name)
    return jsonify(name), 201


class SubscriptionsResource(Resource):
    """Class that assists with managing resource subscriptions."""

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
        """Get subscription.

        Returns:
            All subscription info.
        """
        return Subscription.query.all()

    @marshal_with(SubscriptionDefinition)
    def post(self):
        """Post subscriptions.

        Raises:
            Conflict: SQLAlchemy has detect a IntegirityError.
            UnprocessableEntity: if the SubscriptionDefintion is unprocessable.

        Returns:
            The subscription posted and status.
        """
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
    """Class that assists with managing resource subscriptions."""

    def delete(self, subscription_id):
        """Post subscriptions.

        Args:
            subscription_id: Subscription ID.

        Returns:
            The subscription delted and status.
        """
        Subscription.query.filter_by(id=subscription_id).delete()
        db.session.commit()

        return "", 204


orchestrationsAPI.add_resource(SubscriptionsResource, "/subscriptions")
orchestrationsAPI.add_resource(SubscriptionResource, "/subscriptions/<id>")
