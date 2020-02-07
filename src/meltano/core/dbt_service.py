import asyncio
import logging
import sys
import os
from typing import Optional

from .config_service import ConfigService
from .db import project_engine
from .plugin import PluginType, PluginRef
from .plugin_invoker import invoker_factory
from .venv_service import VenvService
from .logging import capture_subprocess_output
from .elt_context import ELTContext


class DbtService:
    def __init__(self, project, config_service=None):
        self.project = project
        self.config_service = config_service or ConfigService(project)
        self.project_dir = self.project.root_dir("transform")
        self.profile_dir = self.project_dir.joinpath("profile")

        self._plugin = None

    @property
    def exec_path(self):
        return self.venv_service.exec_path("dbt", namespace=PluginType.TRANSFORMERS)

    @property
    def plugin(self):
        if not self._plugin:
            self._plugin = self.config_service.find_plugin("dbt")

        return self._plugin

    def project_args(self):
        return [
            "--project-dir",
            str(self.project_dir),
            "--profiles-dir",
            str(self.profile_dir),
            "--profile",
            "meltano",
        ]

    def dbt_invoker(self) -> "PluginInvoker":
        _, self._Session = project_engine(self.project)
        session = self._Session()

        try:
            return invoker_factory(
                self.project, self.plugin, prepare_with_session=session
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
                f"dbt {cmd} didn't exit cleanly. Exit code: {handle.returncode}"
            )

    async def deps(self):
        await self.invoke("deps")

    async def clean(self):
        await self.invoke("clean")

    async def compile(self, models=None, **kwargs):
        params = self.project_args()

        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        await self.invoke("compile", *params, **kwargs)

    async def run(self, models=None, **kwargs):
        params = self.project_args()

        if models:
            # Always include the my_meltano_project model
            all_models = f"{models} my_meltano_project"
            params.extend(["--models", all_models])

        await self.invoke("run", *params, **kwargs)
