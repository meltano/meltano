import asyncio
import logging
import sys
from typing import Optional

from .config_service import ConfigService
from .db import project_engine
from .plugin import PluginType
from .plugin_invoker import invoker_factory
from .venv_service import VenvService
from .logging import capture_subprocess_output
from .elt_context import ELTContext


class DbtService:
    def __init__(self, project):
        self.project = project
        self._plugin = ConfigService(project).find_plugin(
            "dbt", PluginType.TRANSFORMERS
        )
        self.profile_dir = self.project.root_dir("transform", "profile")

    @property
    def exec_path(self):
        return self.venv_service.exec_path("dbt", namespace=PluginType.TRANSFORMERS)

    def dbt_invoker(self) -> "PluginInvoker":
        _, self._Session = project_engine(self.project)
        session = self._Session()

        try:
            return invoker_factory(
                self.project, self._plugin, prepare_with_session=session
            )
        finally:
            session.close()

    async def invoke(self, cmd, *args, **kwargs):
        invoker = self.dbt_invoker()
        handle = await invoker.invoke_async(
            cmd,
            *args,
            **kwargs,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await asyncio.wait([
                capture_subprocess_output(handle.stdout, sys.stdout),
                capture_subprocess_output(handle.stderr, sys.stderr),
                handle.wait(),
            ],
            return_when=asyncio.ALL_COMPLETED)

        if handle.returncode:
            raise Exception(
                f"dbt {cmd} didn't exit cleanly. Exit code: {handle.returncode}"
            )

    async def docs(self, *args, **kwargs):
        await self.invoke("docs", *args, env={'MELTANO_LOAD_SCHEMA': "<meltano>"})

    async def deps(self):
        await self.invoke("deps")

    async def compile(self, models=None, **kwargs):
        params = ["--profiles-dir", str(self.profile_dir), "--profile", "meltano"]
        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        await self.invoke("compile", *params, **kwargs)

    async def run(self, models=None, **kwargs):
        params = ["--profiles-dir", str(self.profile_dir), "--profile", "meltano"]

        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        await self.invoke("run", *params, **kwargs)
