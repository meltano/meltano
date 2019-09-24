# import meltano.api.config as _config
# from meltano.core.project import Project
# from meltano.api.workers import MeltanoBackgroundCompiler, AirflowWorker

bind = ["0.0.0.0:5000"]
#pidfile = ".meltano/run/gunicorn.pid"
workers = 4
