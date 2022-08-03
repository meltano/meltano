from __future__ import annotations

import asyncio
import sys

from meltano.core.elt_context import ELTContext
from meltano.core.logging import capture_subprocess_output
from meltano.core.plugin import PluginType
from meltano.core.plugin_invoker import PluginInvoker

from . import Runner, RunnerError


class DbtRunner(Runner):
    def __init__(self, elt_context: ELTContext):
        self.context = elt_context

    @property
    def project(self):
        return self.context.project

    @property
    def plugin_context(self):
        return self.context.transformer

    async def invoke(self, dbt: PluginInvoker, *args, log=None, **kwargs):
        """Call the dbt executable with the given arguments in a new process."""
        log = log or sys.stderr

        try:
            handle = await dbt.invoke_async(
                *args,
                **kwargs,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as err:
            raise RunnerError(f"Cannot start dbt: {err}") from err

        await asyncio.wait(
            [
                asyncio.create_task(coro)
                for coro in (
                    capture_subprocess_output(handle.stdout, log),
                    capture_subprocess_output(handle.stderr, log),
                    handle.wait(),
                )
            ],
            return_when=asyncio.ALL_COMPLETED,
        )

        exitcode = handle.returncode
        if exitcode:
            command = kwargs["command"] or args[0]
            raise RunnerError(
                f"`dbt {command}` failed", {PluginType.TRANSFORMERS: exitcode}
            )

    async def run(self, log=None):
        dbt = self.context.transformer_invoker()

        async with dbt.prepared(self.context.session):
            await self.invoke(dbt, log=log, command="clean")
            await self.invoke(dbt, log=log, command="deps")

            cmd = "compile" if self.context.dry_run else "run"
            await self.invoke(dbt, log=log, command=cmd)
