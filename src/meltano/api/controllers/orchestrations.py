import logging
from datetime import datetime
from flask import Blueprint, request, url_for, jsonify, make_response, Response

from meltano.core.plugin import PluginType, PluginRef
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
from meltano.cli.add import extractor


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


@orchestrationsBP.route("/run", methods=["POST"])
def run():
    out_nl = "\n"
    run_output = StringIO(newline=out_nl)
    incoming = request.get_json()
    extractor_name = incoming["extractor"]
    loader_name = incoming["loader"]
    connection_name = incoming.get("connection_name")
    runner = MeltanoRunner()

    # Use a logging handler to capture the output of the extraction run
    runner.logger.addHandler(logging.StreamHandler(run_output))
    runner.perform(extractor_name, loader_name)

    run_output.write("\nLoad done!")
    run_output.write("\nStarting Transform")

    # use the extractor's name as the model name for the transform operation
    transform_log = run_transform(extractor_name, connection_name)

    if transform_log["status"] != "ok":
        run_output.write("\nERROR")
    else:
        run_output.write(f"\nStatus: {transform_log['status']}")
        run_output.write(f"\nCommand: {transform_log['command']}")

    run_output.write(f"\n\nStatus:{transform_log['output']}\n")
    return jsonify({"append": run_output.getvalue()})


@orchestrationsBP.route("/extract/<extractor_name>", methods=["POST"])
def extract(extractor_name: str) -> Response:
    """
    endpoint that performs extraction of the selected datasource to the .csv file(s)
    stored on disk in the /static/tmp/ directory)
    """
    runner = MeltanoRunner()
    csv_files = runner.perform(extractor_name, "csv")
    csv_files_url = [
        url_for("static", filename=f"tmp/{file_name}") for file_name in csv_files
    ]
    return jsonify(
        {"extractor_name": extractor_name, "output_file_paths": csv_files_url}
    )


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


@orchestrationsBP.route("/load/<loader_name>", methods=["POST"])
def load(loader_name: str) -> Response:
    """
    endpoint that performs load of the .csv file(s)(stored on disk in the /static/tmp/ directory)
    of the selected extractor  into the selected loader
    :param loader_name: the name of the loader to use in this request
    """
    incoming = request.get_json()
    try:
        extractor_name = incoming["extractor"]
        extractor_class = MeltanoRunner.import_cls(EXTRACTOR_REGISTRY[extractor_name])
        extractor = extractor_class()
    except KeyError:
        return make_response(
            jsonify(
                {
                    "response": "extractor not found",
                    "available_extractors": list(EXTRACTOR_REGISTRY.keys()),
                }
            ),
            404,
        )
    try:
        loader_class = MeltanoRunner.import_cls(LOADER_REGISTRY[loader_name])
    except KeyError:
        return make_response(
            jsonify(
                {
                    "response": "Loader not found",
                    "available_loaders": list(LOADER_REGISTRY.keys()),
                }
            ),
            404,
        )

    extractor_temp_files = [
        filename
        for filename in os.listdir(TEMP_FOLDER)
        if filename.startswith(extractor_name)
    ]
    for file_path in extractor_temp_files:
        filename = os.path.splitext(file_path)[0]
        entity_name = filename.split("--")[1]
        loader = loader_class(entity_name=entity_name, extractor=extractor)
        loader.schema_apply()
        datetime_cols = [
            col.name
            for col in loader.table.columns
            if isinstance(col.type, DATETIME_TYPES_TO_PARSE)
        ]
        df = pd.read_csv(
            os.path.join(TEMP_FOLDER, file_path), parse_dates=datetime_cols
        )
        df.replace({pd.NaT: None}, inplace=True)
        loader.load(df=df)
    return jsonify({"response": "done", "inserted_files": extractor_temp_files})


@orchestrationsBP.route("/transform/<topic_name>", methods=["POST"])
def transform(model_name):
    """
    {
        'connection_name': 'prod_dw',
    }
    Looks up the credential by the name of the datastore passed to the api

    Sets the environment variables and runs dbt in a subprocess for the given model
    dbt run --profiles-dir profile --target meltano_analyze --models <model_name>
    """
    incoming = request.get_json()
    connection_name = incoming.get("connection_name")

    return jsonify(run_transform(topic_name, connection_name))


def run_transform(topic_name, connection_name):
    settings = Settings.query.first()
    settings_connections = settings.settings["connections"]
    connection = next(
        (item for item in settings_connections if item["name"] == connection_name), None
    )

    if not connection:
        return {
            "status": "error",
            "output": f"Connection {connection_name} not found",
            "command": "",
        }

    new_env = os.environ.copy()

    if connection["dialect"] == "postgresql":
        new_env["PG_ADDRESS"] = connection["host"]
        new_env["PG_PORT"] = str(connection["port"])
        new_env["PG_USERNAME"] = connection["username"]
        new_env["PG_PASSWORD"] = str(connection["password"])
        new_env["PG_DATABASE"] = connection["database"]
        new_env["PG_SCHEMA"] = connection["schema"]

    run_command = [
        "dbt",
        "run",
        "--profiles-dir",
        f"{PROFILES_DIR}",
        "--target",
        "meltano_analyze",
    ]
    if model_name:
        run_command.extend(["--models", f"{topic_name}"])

    work_dir = os.getcwd()
    os.chdir(os.path.join(PROJECT_ROOT_DIR, TRANSFORM_DIR))

    command = " ".join(run_command)
    proc = subprocess.Popen(command, env=new_env, shell=True, stdout=subprocess.PIPE)
    transform_log = proc.stdout.read()

    os.chdir(work_dir)

    return {
        "command": str(command),
        "output": transform_log.decode("utf-8"),
        "status": "ok",
    }


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
