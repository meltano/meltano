import os
import asyncio
import logging
import sys
from io import StringIO

from . import Runner
from meltano.core.error import SubprocessError
from meltano.core.project import Project
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker
from meltano.core.db import project_engine
from meltano.core.logging import capture_subprocess_output
from meltano.core.elt_context import ELTContext


class DbtRunner(Runner):
    def __init__(self, elt_context: ELTContext):
        self.context = elt_context

    @property
    def project(self):
        return self.context.project

    @property
    def plugin(self):
        return self.context.transformer

    async def invoke(self, dbt: PluginInvoker, cmd, *args, **kwargs):
        handle = await dbt.invoke_async(
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

    def run(self, session, dry_run=False):
        dbt = self.context.transformer_invoker()
        dbt.prepare(session)

        # Get an asyncio event loop and use it to run the dbt commands
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.invoke(dbt, "clean"))
        loop.run_until_complete(self.invoke(dbt, "deps"))

        cmd = "compile" if dry_run else "run"
        loop.run_until_complete(
            self.invoke(dbt, cmd, "--models", str(self.plugin.config["models"]))
        )
