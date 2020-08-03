import asyncio
import json
import logging
import sqlalchemy
import shutil
from flask import request, url_for, jsonify, make_response, Response, send_file
from flask_restful import Api, Resource, fields, marshal, marshal_with
from werkzeug.exceptions import Conflict, UnprocessableEntity

from meltano.core.job import JobFinder, State
from meltano.core.behavior.canonical import Canonical
from meltano.core.plugin import PluginRef, Profile
from meltano.core.plugin.error import PluginExecutionError, PluginLacksCapabilityError
from meltano.core.plugin.settings_service import (
    PluginSettingsService,
    SettingValueStore,
)
from meltano.core.plugin_discovery_service import (
    PluginDiscoveryService,
    PluginNotFoundError,
)
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.config_service import ConfigService
from meltano.core.schedule_service import (
    ScheduleService,
    ScheduleAlreadyExistsError,
    ScheduleDoesNotExistError,
)
from meltano.core.utils import flatten, iso8601_datetime, slugify
from meltano.core.logging import (
    JobLoggingService,
    MissingJobLogException,
    SizeThresholdJobLogException,
)
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.security.auth import block_if_readonly
from meltano.api.models import db
from meltano.api.models.subscription import Subscription
from meltano.api.json import freeze_keys
from meltano.api.executor import run_elt
from flask_security import roles_required
from .errors import InvalidFileNameError
from .upload_helper import InvalidFileTypeError, InvalidFileSizeError, UploadHelper
from .utils import enforce_secure_filename


def decorate_profile_config(profile):
    profile["config"] = freeze_keys(profile.get("config", {}))

    config_metadata = profile.get("config_metadata", {})
    for key, metadata in config_metadata.items():
        try:
            metadata["source_label"] = metadata["source"].label
            metadata["auto_store_label"] = metadata["auto_store"].label
        except KeyError:
            pass

    profile["config_metadata"] = freeze_keys(config_metadata)


def validate_plugin_config(
    plugin: PluginRef, name, value, project: Project, settings: PluginSettingsService
):
    setting_def = settings.find_setting(name)
    # we want to prevent the edition of protected settings from the UI
    if setting_def.protected:
        logging.warning("Cannot set a 'protected' setting externally.")
        return False

    if setting_def.kind == "file" and value and value != "":
        uploads_directory = project.extract_dir(plugin.full_name)
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


@orchestrationsBP.errorhandler(ScheduleDoesNotExistError)
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


@orchestrationsBP.errorhandler(InvalidFileNameError)
def _handle(ex):
    return (jsonify({"error": True, "code": f"The file lacks a valid name."}), 400)


@orchestrationsBP.errorhandler(InvalidFileTypeError)
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


@orchestrationsBP.errorhandler(InvalidFileSizeError)
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


@orchestrationsBP.errorhandler(MissingJobLogException)
def _handle(ex):
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
    job_id = run_elt(project, schedule_payload)

    return jsonify({"job_id": job_id}), 202


@orchestrationsBP.route(
    "/<plugin_ref:plugin_ref>/configuration/upload-file", methods=["POST"]
)
@block_if_readonly
def upload_plugin_configuration_file(plugin_ref) -> Response:
    """
    Endpoint for uploading a file for a specific plugin's configuration profile
    """

    file = request.files["file"]
    setting_name = enforce_secure_filename(request.form["setting_name"])
    tmp = request.form.get("tmp", False)

    project = Project.find()
    directory = project.extract_dir(
        plugin_ref.full_name, ("tmp" if tmp else ""), setting_name
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
    Endpoint for deleting a file for a specific plugin's configuration profile
    """

    payload = request.get_json()
    setting_name = enforce_secure_filename(payload["setting_name"])
    tmp = payload.get("tmp", False)

    project = Project.find()
    directory = project.extract_dir(
        plugin_ref.full_name, ("tmp" if tmp else ""), setting_name
    )
    shutil.rmtree(directory)

    return jsonify({"setting_name": setting_name}), 200


@orchestrationsBP.route("/<plugin_ref:plugin_ref>/configuration", methods=["GET"])
def get_plugin_configuration(plugin_ref) -> Response:
    """
    Endpoint for getting a plugin's configuration profiles
    """

    project = Project.find()
    config_service = ConfigService(project)
    plugin = config_service.get_plugin(plugin_ref)

    discovery_service = PluginDiscoveryService(project, config_service=config_service)
    settings = PluginSettingsService(
        project,
        plugin,
        config_service=config_service,
        plugin_discovery_service=discovery_service,
        show_hidden=False,
    )

    try:
        plugin_def = discovery_service.find_plugin(plugin.type, plugin.name)
        settings_group_validation = plugin_def.settings_group_validation
    except PluginNotFoundError:
        settings_group_validation = []

    profiles = settings.profiles_with_config(redacted=True, session=db.session)
    for profile in profiles:
        decorate_profile_config(profile)

    return jsonify(
        {
            "profiles": profiles,
            "settings": Canonical.as_canonical(settings.definitions(extras=False)),
            "settings_group_validation": settings_group_validation,
        }
    )


@orchestrationsBP.route(
    "/<plugin_ref:plugin_ref>/configuration/profiles", methods=["POST"]
)
@block_if_readonly
def add_plugin_configuration_profile(plugin_ref) -> Response:
    """
    Endpoint for adding a configuration profile to a plugin
    """
    payload = request.get_json()
    project = Project.find()
    config = ConfigService(project)
    plugin = config.get_plugin(plugin_ref)
    settings = PluginSettingsService(project, plugin, config_service=config)

    # create the new profile for this plugin
    name = payload["name"]
    profile = plugin.add_profile(slugify(name), label=name)

    config.update_plugin(plugin)

    profile_config = settings.profile_with_config(
        profile, redacted=True, session=db.session
    )
    decorate_profile_config(profile_config)

    return jsonify(profile_config)


@orchestrationsBP.route("/<plugin_ref:plugin_ref>/configuration", methods=["PUT"])
@block_if_readonly
def save_plugin_configuration(plugin_ref) -> Response:
    """
    Endpoint for persisting a plugin configuration
    """
    project = Project.find()
    payload = request.get_json()
    config_service = ConfigService(project)
    plugin = config_service.get_plugin(plugin_ref)

    # TODO iterate pipelines and save each, also set this connector's profile (reuse `pipelineInFocusIndex`?)

    settings = PluginSettingsService(
        project, plugin, config_service=config_service, show_hidden=False
    )

    for profile in payload:
        # select the correct profile
        name = profile["name"]
        plugin.use_profile(plugin.get_profile(name))

        for name, value in profile["config"].items():
            if not validate_plugin_config(plugin, name, value, project, settings):
                continue

            if value == "":
                settings.unset(name, session=db.session)
            else:
                settings.set(name, value, session=db.session)

    profiles = settings.profiles_with_config(redacted=True, session=db.session)
    for profile in profiles:
        decorate_profile_config(profile)

    return jsonify(profiles)


@orchestrationsBP.route("/<plugin_ref:plugin_ref>/configuration/test", methods=["POST"])
@block_if_readonly
def test_plugin_configuration(plugin_ref) -> Response:
    """
    Endpoint for testing a plugin configuration's valid connection
    """
    project = Project.find()
    payload = request.get_json()
    config_service = ConfigService(project)
    plugin = config_service.get_plugin(plugin_ref)

    # load the correct profile
    plugin.use_profile(plugin.get_profile(payload.get("profile")))

    settings = PluginSettingsService(
        project, plugin, config_service=config_service, show_hidden=False
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
                prepare_with_session=db.session,
                plugin_settings_service=settings,
            )
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
