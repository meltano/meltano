import asyncio
import logging
import sys

from .config_service import ConfigService
from .db import project_engine
from .plugin import PluginType
from .plugin_invoker import invoker_factory
from .venv_service import VenvService
from .logging import capture_subprocess_output


class DbtService:
    def __init__(self, project):
        self.project = project
        self._plugin = ConfigService(project).find_plugin(
            "dbt", PluginType.TRANSFORMERS
        )
        self.profile_dir = f"{self.project.root}/transform/profile/"
        _, self._Session = project_engine(project)

    @property
    def exec_path(self):
        return self.venv_service.exec_path("dbt", namespace=PluginType.TRANSFORMERS)

    async def compile(self, models=None, **kwargs):
        session = self._Session()
        invoker = invoker_factory(session, self.project, self._plugin)

        try:
            params = ["--profiles-dir", self.profile_dir, "--profile", "meltano"]
            if models:
                # Always include the my_meltano_project model
                all_models = f"{models} my_meltano_project"
                params.extend(["--models", all_models])

            handle = await invoker.invoke_async(
                "compile",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                *params,
                **kwargs,
            )

            # run the dbt compile command, capture the stdout and stderr
            #  and send them to the stdout, stderr set by OutputLogger
            #  so that they are also logged in a log file in real time
            await asyncio.wait(
                [
                    capture_subprocess_output(handle.stdout, sys.stdout),
                    capture_subprocess_output(handle.stderr, sys.stderr),
                    handle.wait(),
                ],
                return_when=asyncio.ALL_COMPLETED,
            )

            if handle.returncode:
                raise Exception(
                    f"dbt compile didn't exit cleanly. Exit code: {handle.returncode}"
                )
        finally:
            session.close()

    async def deps(self):
        session = self._Session()
        invoker = invoker_factory(session, self.project, self._plugin)
        try:
            handle = await invoker.invoke_async(
                "deps", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            # run the dbt deps command and capture the stdout and stderr
            await asyncio.wait(
                [
                    capture_subprocess_output(handle.stdout, sys.stdout),
                    capture_subprocess_output(handle.stderr, sys.stderr),
                    handle.wait(),
                ],
                return_when=asyncio.ALL_COMPLETED,
            )

            if handle.returncode:
                raise Exception(
                    f"dbt deps didn't exit cleanly. Exit code: {handle.returncode}"
                )
        finally:
            session.close()

    async def run(self, models=None, **kwargs):
        session = self._Session()
        invoker = invoker_factory(session, self.project, self._plugin)

        try:
            params = ["--profiles-dir", self.profile_dir, "--profile", "meltano"]
            if models:
                # Always include the my_meltano_project model
                all_models = f"{models} my_meltano_project"
                params.extend(["--models", all_models])

            handle = await invoker.invoke_async(
                "run",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                *params,
                **kwargs,
            )

            # run the dbt run command and capture the stdout and stderr
            await asyncio.wait(
                [
                    capture_subprocess_output(handle.stdout, sys.stdout),
                    capture_subprocess_output(handle.stderr, sys.stderr),
                    handle.wait(),
                ],
                return_when=asyncio.ALL_COMPLETED,
            )

            if handle.returncode:
                raise Exception(
                    f"dbt run didn't exit cleanly. Exit code: {handle.returncode}"
                )
        finally:
            session.close()
