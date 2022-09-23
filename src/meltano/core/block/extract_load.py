"""Basic EL style BlockSet implementation."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, closing
from typing import AsyncIterator

import structlog
from sqlalchemy.orm import Session

from meltano.core.db import project_engine
from meltano.core.elt_context import PluginContext
from meltano.core.job import Job, JobFinder
from meltano.core.job.stale_job_failer import fail_stale_jobs
from meltano.core.logging import JobLoggingService, OutputLogger
from meltano.core.plugin import PluginType
from meltano.core.plugin.project_plugin import ProjectPlugin
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_invoker import PluginInvoker, invoker_factory
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.runner import RunnerError
from meltano.core.state_service import STATE_ID_COMPONENT_DELIMITER, StateService

from .blockset import BlockSet, BlockSetValidationError
from .future_utils import first_failed_future, handle_producer_line_length_limit_error
from .ioblock import IOBlock
from .singer import SingerBlock

logger = structlog.getLogger(__name__)


class BlockSetHasNoStateError(Exception):
    """Occurs when state_service is accessed for ExtractLoadBlocks instance for which no block has state."""


class ELBContext:  # noqa: WPS230
    """ELBContext holds the context for ELB BlockSets."""

    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
        session: Session = None,
        job: Job | None = None,
        full_refresh: bool | None = False,
        force: bool | None = False,
        update_state: bool | None = True,
        state_id_suffix: str | None = None,
        base_output_logger: OutputLogger | None = None,
    ):
        """Use an ELBContext to pass information on to ExtractLoadBlocks.

        Args:
            project: The project to use.
            plugins_service: The plugins service to use.
            session: The session to use.
            job: The job within this context should run.
            full_refresh: Whether this is a full refresh.
            force: Whether to force the execution of the job if it is stale.
            update_state: Whether to update the state of the job.
            state_id_suffix: The state ID suffix to use.
            base_output_logger: The base logger to use.
        """
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

        self.session = session
        self.job = job

        self.full_refresh = full_refresh
        self.force = force
        self.update_state = update_state
        self.state_id_suffix = state_id_suffix

        # not yet used but required to satisfy the interface
        self.dry_run = False
        self.state = None
        self.select_filter = []
        self.catalog = None

        self.base_output_logger = base_output_logger

    @property
    def elt_run_dir(self) -> str:
        """Obtain the run directory for the current job.

        Returns:
            The run directory for the current job.
        """
        if self.job:
            return self.project.job_dir(self.job.job_name, str(self.job.run_id))


class ELBContextBuilder:
    """Build up ELBContexts for ExtractLoadBlocks."""

    def __init__(
        self,
        project: Project,
        plugins_service: ProjectPluginsService = None,
        job: Job | None = None,
    ):
        """Initialize a new `ELBContextBuilder` that can be used to upgrade plugins to blocks for use in a ExtractLoadBlock.

        Args:
            project: the meltano project for the context.
            plugins_service: the plugins service for the context.
            job: the job for this ELT run.
        """
        self.project = project
        self.plugins_service = plugins_service or ProjectPluginsService(project)

        _, session_maker = project_engine(project)
        self.session = session_maker()

        self._job = None
        self._full_refresh = False
        self._state_update = True
        self._force = False
        self._state_id_suffix = None
        self._env = {}
        self._blocks = []

        self._base_output_logger = None

    def with_job(self, job: Job):
        """Set the associated job for the context.

        Args:
            job: the initial job for the context.

        Returns:
            self
        """
        self._job = job
        return self

    def with_full_refresh(self, full_refresh: bool):
        """Set whether this is a full refresh.

        Args:
            full_refresh : whether this is a full refresh.

        Returns:
            self
        """
        self._full_refresh = full_refresh
        return self

    def with_no_state_update(self, no_state_update: bool):
        """Set whether this run should not update state.

        By default we typically attempt to track state. This allows avoiding state management.


        Args:
            no_state_update: whether this run should update state.

        Returns:
            self
        """
        self._state_update = not no_state_update
        return self

    def with_force(self, force: bool):
        """Set whether the execution of the job should be forced if it is stale.

        Args:
            force: Whether to force the execution of the job if it is stale.

        Returns:
            self
        """
        self._force = force
        return self

    def with_state_id_suffix(self, state_id_suffix: str):
        """Set a state ID suffix for this run.

        Args:
            state_id_suffix: The suffix value.

        Returns:
            self
        """
        self._state_id_suffix = state_id_suffix
        return self

    def make_block(
        self,
        plugin: ProjectPlugin,
        plugin_args: list[str] | None = None,
    ) -> SingerBlock:
        """Create a new `SingerBlock` object, from a plugin.

        Args:
            plugin: The plugin to be executed.
            plugin_args: The arguments to be passed to the plugin.

        Returns:
            The new `SingerBlock` object.
        """
        ctx = self.plugin_context(plugin, env=self._env.copy())

        block = SingerBlock(
            block_ctx=ctx,
            project=self.project,
            plugins_service=self.plugins_service,
            plugin_invoker=self.invoker_for(ctx),
            plugin_args=plugin_args,
        )
        self._blocks.append(block)
        self._env.update(ctx.env)
        return block

    def plugin_context(
        self,
        plugin: ProjectPlugin,
        env: dict | None = None,
    ) -> PluginContext:
        """Create context object for a plugin.

        Args:
            plugin: The plugin to create the context for.
            env: Environment override dictionary.

        Returns:
            A new `PluginContext` object.
        """
        return PluginContext(
            plugin=plugin,
            settings_service=PluginSettingsService(
                self.project,
                plugin,
                plugins_service=self.plugins_service,
                env_override=env,
            ),
            session=self.session,
        )

    def invoker_for(
        self,
        plugin_context: PluginContext,
    ) -> PluginInvoker:
        """Create an invoker for a plugin from a PluginContext.

        Args:
            plugin_context: The plugin context to pass to the invoker_factory.

        Returns:
            A new `PluginInvoker` object.
        """
        return invoker_factory(
            self.project,
            plugin_context.plugin,
            context=self.context(),
            run_dir=self.elt_run_dir,
            plugins_service=self.plugins_service,
            plugin_settings_service=plugin_context.settings_service,
        )

    @property
    def elt_run_dir(self) -> str:
        """Get the run directory for the current job.

        Returns:
            The run directory for the current job.
        """
        if self._job:
            return self.project.job_dir(self._job.job_name, str(self._job.run_id))

    def context(self) -> ELBContext:
        """Create an ELBContext object from the current builder state.

        Returns:
            A new `ELBContext` object.
        """
        return ELBContext(
            project=self.project,
            plugins_service=self.plugins_service,
            session=self.session,
            job=self._job,
            full_refresh=self._full_refresh,
            force=self._force,
            update_state=self._state_update,
            state_id_suffix=self._state_id_suffix,
            base_output_logger=self._base_output_logger,
        )


class ExtractLoadBlocks(BlockSet):  # noqa: WPS214
    """A basic BlockSet interface implementation that supports running basic EL (extract, load) patterns."""

    def __init__(
        self,
        context: ELBContext,
        blocks: tuple[IOBlock],
    ):
        """Initialize a basic BlockSet suitable for executing ELT tasks.

        Args:
            context: the elt context to use for this elt run.
            blocks: the IOBlocks that should be used for this elt run.
        """
        self.context = context
        self.blocks = blocks
        self.project_settings_service = ProjectSettingsService(
            self.context.project,
            config_service=self.context.plugins_service.config_service,
        )

        self.output_logger = OutputLogger(None)

        if not self.context.project.active_environment:
            self.context.job = None

        elif self.context.update_state:
            state_id = generate_state_id(
                self.context.project, self.context.state_id_suffix, self.head, self.tail
            )
            self.context.job = Job(job_name=state_id)
            job_logging_service = JobLoggingService(self.context.project)
            log_file = job_logging_service.generate_log_name(
                self.context.job.job_name, self.context.job.run_id
            )
            self.output_logger = OutputLogger(log_file)

        self._process_futures = None
        self._stdout_futures = None
        self._stderr_futures = None
        self._errors = []
        self._state_service = None

    def has_state(self) -> bool:
        """Check to see if any block in this BlockSet has 'state' capability.

        Returns:
            bool indicating whether BlockSet has 'state' capability
        """
        for block in self.blocks:
            if block.has_state:
                return True
        return False

    @property
    def state_service(self) -> StateService:
        """Get StateService for managing state for this BlockSet.

        Returns:
            A StateService using this BlockSet's context's session

        Raises:
            BlockSetHasNoStateError: if no Block in this BlockSet has state capability
        """
        if not self._state_service:
            if self.has_state():
                self._state_service = StateService(self.context.session)
            else:
                raise BlockSetHasNoStateError()
        return self._state_service

    def index_last_input_done(self) -> int:
        """Return index of the block furthest from the start that has exited and required input.

        Returns:
            The index of the block furthest from the start that has exited and required input.
        """
        for idx, block in reversed(list(enumerate(self.blocks))):
            if block.requires_input and block.proxy_stderr.done():
                return idx

    def upstream_complete(self, index: int) -> bool:
        """Return whether blocks upstream from a given block index are already done.

        Args:
            index: The index of the block to check upstream from.

        Returns:
            True if all upstream blocks are done, False otherwise.
        """
        for idx, block in enumerate(self.blocks):
            if idx >= index:
                return True
            if block.process_future.done():
                continue
            return False

    async def upstream_stop(self, index) -> None:
        """Stop all blocks upstream of a given index.

        Args:
            index: The index of the block to stop upstream from.
        """
        for block in reversed(self.blocks[:index]):
            await block.stop()

    async def process_wait(
        self, output_exception_future: asyncio.Task | None, subset: int = None
    ) -> set[asyncio.Task]:
        """Wait on all process futures in the block set.

        Args:
            output_exception_future: additional future to wait on for output exceptions.
            subset: the subset of blocks to wait on.

        Returns:
            The set of all process futures + optional output exception futures.
        """
        futures = list(self.process_futures[subset:])
        if output_exception_future:
            futures.append(output_exception_future)

        done, _ = await asyncio.wait(
            futures,
            return_when=asyncio.FIRST_COMPLETED,
        )
        return done

    def validate_set(self) -> None:  # noqa: WPS231, WPS238
        """Validate a ExtractLoad block set to ensure its valid and runnable.

        Raises:
            BlockSetValidationError: if the block set is not valid.
        """
        if not self.blocks:
            raise BlockSetValidationError("No blocks in set.")

        if self.head.consumer:
            raise BlockSetValidationError("first block in set should not be consumer")

        if self.tail.producer:
            raise BlockSetValidationError("last block in set should not be a producer")

        for block in self.intermediate:
            if not block.consumer or not block.producer:
                raise BlockSetValidationError(
                    "intermediate blocks must be producers AND consumers"
                )

    async def execute(self) -> None:
        """Build the IO chain and execute the actual ELT task."""
        async with self._start_blocks():
            await self._link_io()
            manager = ELBExecutionManager(self)
            await manager.run()

    async def run(self) -> None:
        """Run the ELT task."""
        if self.context.job:
            # TODO: legacy `meltano elt` style logging should be deprecated
            legacy_log_handler = self.output_logger.out("meltano", logger)
            with legacy_log_handler.redirect_logging():
                await self.run_with_job()
                return
        else:
            logger.warning(
                "No active environment, proceeding with stateless run! See https://docs.meltano.com/reference/command-line-interface#run for details."
            )
        await self.execute()

    async def run_with_job(self) -> None:
        """Run the ELT task within the context of a job.

        Raises:
            RunnerError: if failures are encountered during execution or if the underlying pipeline/job is already running.
        """
        job = self.context.job
        fail_stale_jobs(self.context.session, job.job_name)
        if not self.context.force:
            existing = JobFinder(job.job_name).latest_running(self.context.session)
            if existing:
                raise RunnerError(
                    f"Another '{job.job_name}' pipeline is already running which started at {existing.started_at}. "
                    + "To ignore this check use the '--force' option."
                )

        with closing(self.context.session) as session:
            async with job.run(session):
                await self.execute()

    async def terminate(self, graceful: bool = False) -> None:
        """Terminate an in flight ExtractLoad execution, potentially disruptive.

        Not actually implemented yet.

        Args:
            graceful: Whether or not the BlockSet should try to gracefully quit.

        Raises:
            NotImplementedError: if graceful termination is not implemented.
        """
        if graceful:
            raise NotImplementedError

        for block in self.blocks:
            await block.stop(kill=True)

    @property
    def process_futures(self) -> list[asyncio.Task]:
        """Return the futures of the blocks subprocess calls.

        Returns:
            The list of all process futures.
        """
        if self._process_futures is None:
            self._process_futures = [block.process_future for block in self.blocks]
        return self._process_futures

    @property
    def stdout_futures(self) -> list[asyncio.Task]:
        """Access the futures of the blocks stdout proxy tasks.

        Returns:
            The list of all stdout futures.
        """
        if self._stdout_futures is None:
            self._stdout_futures = [block.proxy_stdout() for block in self.blocks]
        return self._stdout_futures

    @property
    def stderr_futures(self) -> list[asyncio.Task]:
        """Access the futures of the blocks stderr proxy tasks.

        Returns:
            The list of all stderr futures.
        """
        if self._stderr_futures is None:
            self._stderr_futures = [block.proxy_stderr() for block in self.blocks]
        return self._stderr_futures

    @property
    def head(self) -> IOBlock:
        """Obtain the first block in the block set.

        Returns:
            The first block in the block set.
        """
        return self.blocks[0]

    @property
    def tail(self) -> IOBlock:
        """Obtain the last block in the block set.

        Returns:
            The last block in the block set.
        """
        return self.blocks[-1]

    @property
    def intermediate(self) -> tuple[IOBlock]:
        """Obtain the intermediate blocks in the set - excluding the first and last block.

        Returns:
            The intermediate blocks in the block set.
        """
        return self.blocks[1:-1]

    @asynccontextmanager
    async def _start_blocks(self) -> AsyncIterator[None]:
        """Start the blocks in the block set.

        Yields:
            None
        """
        try:  # noqa:  WPS229
            for block in self.blocks:
                await block.pre(self.context)
                await block.start()
            yield
        finally:
            await self._cleanup()

    async def _cleanup(self) -> None:
        for block in self.blocks:
            await block.post()

    async def _link_io(self) -> None:  # noqa: WPS231
        """Link the blocks in the set together.

        This method does one last validation check to ensure that a consumer has a producer upstream.

        Raises:
            BlockSetValidationError: if consumer does not have an upstream producer.
        """
        for idx, block in enumerate(self.blocks):
            logger_base = logger.bind(
                consumer=block.consumer,
                producer=block.producer,
                string_id=block.string_id,
                cmd_type="elb",
            )
            if logger.isEnabledFor(logging.DEBUG):
                block.stdout_link(
                    self.output_logger.out(
                        block.string_id,
                        logger_base.bind(stdio="stdout"),
                    )
                )
            block.stderr_link(
                self.output_logger.out(
                    block.string_id,
                    logger_base.bind(stdio="stderr"),
                )
            )
            if block.consumer:
                if idx != 0 and self.blocks[idx - 1].producer:
                    self.blocks[idx - 1].stdout_link(
                        block.stdin
                    )  # link previous blocks stdout with current blocks stdin
                else:
                    raise BlockSetValidationError(
                        "run step requires input but has no upstream"
                    )


class ELBExecutionManager:
    """Execution manager for ExtractLoadBlock sets."""

    def __init__(self, elb: ExtractLoadBlocks) -> None:
        """Initialize the ELBExecutionManager which will handle the actual runtime management of the block set.

        Args:
            elb: The ExtractLoadBlocks to manage.
        """
        self.elb = elb
        self.stream_buffer_size = self.elb.project_settings_service.get(
            "elt.buffer_size"
        )
        self.line_length_limit = self.stream_buffer_size // 2

        self._producer_code = None
        self._consumer_code = None
        self._intermediate_codes: dict[str, int] = {}

    async def run(self) -> None:
        """Run is used to actually perform the execution of the ExtractLoadBlock set.

        That entails starting the blocks, waiting for them to complete, ensuring that exceptions are handled, and
        stopping blocks or waiting for IO to complete as appropriate. Expect a RunnerError to be raised if any of
        the blocks exit with a non 0 exit code.
        """
        await self._wait_for_process_completion(self.elb.head)
        _check_exit_codes(
            self._producer_code, self._consumer_code, self._intermediate_codes
        )

    async def _complete_upstream(self) -> None:
        """Wait for the upstream blocks to complete."""
        producer = self.elb.head
        consumer = self.elb.tail

        if self.elb.upstream_complete(len(self.elb.blocks) - 1):
            self._producer_code = producer.process_future.result()
        else:
            # If the last consumer (target) completes before the upstream producers, it failed before processing all
            # output. So we should kill the upstream producers and cancel output processing since there's no final
            # destination to forward output to.
            await self.elb.upstream_stop(len(self.elb.blocks) - 1)
            # Pretend the producer (tap) finished successfully since it didn't itself fail
            self._producer_code = 0
        # Wait for all buffered consumer (target) output to be processed
        await asyncio.wait([consumer.proxy_stdout(), consumer.proxy_stderr()])

    async def _wait_for_process_completion(  # noqa: WPS213 WPS217
        self, current_head: IOBlock
    ) -> tuple[int, int] | None:
        """Wait for the current head block to complete or for an error to occur.

        Args:
            current_head: The current head block

        Returns:
            A tuple of the producer exit code and the consumer exit code

        Raises:
            RunnerError: if any intermediate blocks failed.
            exception: if any of the output futures encountered an exception.
        """
        start_idx = self.elb.blocks.index(current_head)
        remaining_blocks = self.elb.blocks[start_idx:]

        if remaining_blocks is None or current_head == self.elb.tail:
            return

        stdout_futures = [block.proxy_stdout() for block in remaining_blocks]
        stderr_futures = [block.proxy_stderr() for block in remaining_blocks]

        output_exception_future = asyncio.ensure_future(
            asyncio.wait(
                [*stdout_futures, *stderr_futures],
                return_when=asyncio.FIRST_EXCEPTION,
            )
        )

        logger.debug("waiting for process completion or exception")
        done = await self.elb.process_wait(output_exception_future, start_idx)

        output_futures_failed = first_failed_future(output_exception_future, done)
        if output_futures_failed:
            # Special behavior for a producer stdout handler raising a line length limit error.
            if self.elb.head.proxy_stdout() == output_futures_failed:
                handle_producer_line_length_limit_error(
                    output_futures_failed.exception(),
                    line_length_limit=self.line_length_limit,
                    stream_buffer_size=self.stream_buffer_size,
                )
            raise output_futures_failed.exception()
        else:
            # If all the output handlers completed without raising an exception,
            # we still need to wait for all the underlying block processes to complete.
            # note that since all output handlers completed we DO NOT need to wait for any output futures!
            done = await self.elb.process_wait(None, start_idx)
        if self.elb.tail.process_future.done():
            logger.debug("tail consumer completed first")
            self._consumer_code = self.elb.tail.process_future.result()
            await self._complete_upstream()
        elif current_head.process_future.done():
            logger.debug(
                "head producer completed first as expected", name=current_head.string_id
            )
            await self._handle_head_completed(current_head, start_idx)
        else:
            logger.warning("Intermediate block in sequence failed.")
            await self._stop_all_blocks(start_idx)
            raise RunnerError(
                "Unexpected completion sequence in ExtractLoadBlock set. Intermediate block (likely a mapper) failed.",
                {
                    PluginType.EXTRACTORS: 1,
                    PluginType.LOADERS: 1,
                },
            )

    async def _handle_head_completed(
        self, current_head: IOBlock, start_idx: int
    ) -> None:
        next_head: IOBlock = self.elb.blocks[start_idx + 1]

        if current_head is self.elb.head:
            self._producer_code = current_head.process_future.result()
        else:
            self._intermediate_codes[
                current_head.string_id
            ] = current_head.process_future.result()

        await asyncio.wait([current_head.proxy_stdout(), current_head.proxy_stderr()])
        # Close next inline stdin so downstream can cascade and complete naturally
        await next_head.close_stdin()

        if next_head is self.elb.tail:
            logger.debug("tail consumer is next block, wrapping up")
            # Wait for all buffered target output to be processed
            await asyncio.wait([next_head.proxy_stdout(), next_head.proxy_stderr()])

            # Wait for target process future to complete
            await next_head.process_future
            self._consumer_code = next_head.process_future.result()
            return  # break our recursion

        await self._wait_for_process_completion(next_head)

    async def _stop_all_blocks(self, idx: int = 0) -> None:
        """Close stdin and stop all blocks inclusive of index.

        Args:
            idx: starting index of the block's to stop.
        """
        for block in self.elb.blocks[idx:]:
            await block.close_stdin()
            await block.stop()


def _check_exit_codes(  # noqa: WPS238
    producer_code: int, consumer_code: int, intermediate_codes: dict[str, int]
) -> None:
    """Check exit codes for failures, and raise the appropriate RunnerError if needed.

    Args:
        producer_code: exit code of the producer (tap)
        consumer_code: exit code of the consumer (target)
        intermediate_codes: exit codes of the intermediate blocks (mappers)

    Raises:
        RunnerError: if the producer, consumer, or mapper exit codes are non-zero
    """
    if producer_code and consumer_code:
        raise RunnerError(
            "Extractor and loader failed",
            {PluginType.EXTRACTORS: producer_code, PluginType.LOADERS: consumer_code},
        )

    if producer_code:
        raise RunnerError("Extractor failed", {PluginType.EXTRACTORS: producer_code})

    if consumer_code:
        raise RunnerError("Loader failed", {PluginType.LOADERS: consumer_code})

    failed_mappers = []
    for mapper_id in intermediate_codes.keys():
        if intermediate_codes[mapper_id]:
            failed_mappers.append({mapper_id: intermediate_codes[mapper_id]})

    if failed_mappers:
        raise RunnerError("Mappers failed", failed_mappers)


def generate_state_id(
    project: Project, state_id_suffix: str | None, consumer: IOBlock, producer: IOBlock
) -> str:
    """Generate a state id based on a project active environment and consumer and producer names.

    Args:
        project: Project to retrieve active environment from.
        state_id_suffix: State ID suffix value.
        consumer: Consumer block.
        producer: Producer block.

    Returns:
        State id string.

    Raises:
        RunnerError: if the project does not have an active environment.
    """
    if not project.active_environment:
        raise RunnerError(
            "No active environment for invocation, but requested state id"
        )

    state_id_components = [
        project.active_environment.name,
        f"{consumer.string_id}-to-{producer.string_id}",
        state_id_suffix or project.active_environment.state_id_suffix,
    ]

    if any(c for c in state_id_components if c and STATE_ID_COMPONENT_DELIMITER in c):
        raise RunnerError(
            f"Cannot generate a state ID from components containing the delimiter string '{STATE_ID_COMPONENT_DELIMITER}'"
        )

    return STATE_ID_COMPONENT_DELIMITER.join(c for c in state_id_components if c)
