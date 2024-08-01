from __future__ import annotations  # noqa: D100

import asyncio
import sys
import typing as t

from meltano.core.logging import capture_subprocess_output
from meltano.core.plugin import PluginType

from . import Runner, RunnerError

if t.TYPE_CHECKING:
    from meltano.core.elt_context import ELTContext
    from meltano.core.plugin_invoker import PluginInvoker


class DbtRunner(Runner):  # noqa: D101
    def __init__(self, elt_context: ELTContext):  # noqa: D107
        self.context = elt_context

    @property
    def project(self):  # noqa: ANN201, D102
        return self.context.project

    @property
    def plugin_context(self):  # noqa: ANN201, D102
        return self.context.transformer

    async def invoke(self, dbt: PluginInvoker, *args, log=None, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
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
            raise RunnerError(f"Cannot start dbt: {err}") from err  # noqa: EM102

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

        if exitcode := handle.returncode:
            command = kwargs["command"] or args[0]
            raise RunnerError(
                f"`dbt {command}` failed",  # noqa: EM102
                {PluginType.TRANSFORMERS: exitcode},
            )

    async def run(self, log=None) -> None:  # noqa: ANN001, D102
        dbt = self.context.transformer_invoker()

        async with dbt.prepared(self.context.session):
            await self.invoke(dbt, log=log, command="clean")
            await self.invoke(dbt, log=log, command="deps")

            cmd = "compile" if self.context.dry_run else "run"
            await self.invoke(dbt, log=log, command=cmd)
