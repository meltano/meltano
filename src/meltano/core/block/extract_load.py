import asyncio
from asyncio import Task
from contextlib import suppress
from typing import List, Set, Tuple

from meltano.core.elt_context import ELTContextBuilder
from meltano.core.plugin import PluginType
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.runner import RunnerError

from .error import BlockSetValidationError
from .future_utils import first_failed_future, handle_producer_line_length_limit_error
from .ioblock import IOBlock


class ExtractLoadBlocks:
    def __init__(self, context: ELTContextBuilder, blocks: Tuple[IOBlock]):
        self.context = context
        self.blocks = blocks
        self.project_settings_service = ProjectSettingsService(
            self.context.project,
            config_service=self.context.plugins_service.config_service,
        )

        self._process_futures = None
        self._stdout_futures = None
        self._stderr_futures = None
        self._has_io = self._series_has_io()
        self._errors = []

    def _series_has_io(self) -> bool:
        for block in self.blocks:
            if block.consumer or block.producer:
                return True
        return False

    @property
    def process_futures(self) -> List[Task]:
        if self._process_futures is None:
            self._process_futures = [block.process_future for block in self.blocks]
        return self._process_futures

    @property
    def stdout_futures(self) -> List[Task]:
        if self._stdout_futures is None:
            self._stdout_futures = [block.proxy_stdout() for block in self.blocks]
        return self._stdout_futures

    @property
    def stderr_futures(self) -> List[Task]:
        if self._stderr_futures is None:
            self._stderr_futures = [block.proxy_stderr() for block in self.blocks]
        return self._stderr_futures

    def index_last_input_done(self) -> int:
        """Return index of the block furthest from the start that has exited and required input."""
        for idx, block in reversed(list(enumerate(self.blocks))):
            if block.requires_input and block.proxy_stderr.done():
                return idx

    def upstream_complete(self, index: int) -> bool:
        """Return whether blocks upstream from a given block index are already done."""
        for idx, block in enumerate(self.blocks):
            if idx >= index:
                return True
            if block.process_future.done():
                continue
            return False

    async def process_wait(
        self, output_exception_future: Task, subset: int = None
    ) -> Set[Task]:
        """Wait on all process futures in the block set."""
        done, _ = await asyncio.wait(
            [*self.process_futures[:subset], output_exception_future],
            return_when=asyncio.FIRST_COMPLETED,
        )
        return done

    async def _upstream_stop(self, index):
        """Stop all blocks upstream of a given index."""
        for block in reversed(self.blocks[:index]):
            await block.stop()

    @property
    def head(self) -> IOBlock:  # TODO: should be Producer block
        return self.blocks[0]

    @property
    def tail(self) -> IOBlock:  # TODO: should be Consumer block
        return self.blocks[-1]

    @property
    def intermediate(self) -> IOBlock:
        return self.blocks[1:-1]

    def validate_set(self) -> None:
        # TODO: this method might not even need to exist here, whatever creates ExtractLoadBlock() should
        # probably pre-validate, but for MVP/testing its handy.

        if self.head.consumer:
            raise BlockSetValidationError("first block in set should not be consumer")

        if self.tail.producer:
            raise BlockSetValidationError("last block in set should not be a producer")

        for block in self.intermediate:
            if not block.consumer or not block.producer:
                raise BlockSetValidationError(
                    "intermediate blocks must be producers AND consumers"
                )

    async def run(self, session) -> bool:
        try:  # noqa: WPS229
            await self._start_blocks(session)
            await self._link_io()
            await experimental_run(self, self.project_settings_service)
            return True
        finally:
            self._cleanup()

    async def _start_blocks(self, session):
        for block in self.blocks:
            await block.pre({"session": session})
            await block.start()

    async def _cleanup(self):
        for block in self.blocks:
            await block.post()

    async def _link_io(self) -> None:
        for idx, block in enumerate(self.blocks):
            if block.consumer:
                # TODO: this check is redundent if validate_set has been called. So we should use that probably.
                if idx != 0 and self.blocks[idx - 1].producer:
                    self.blocks[idx - 1].stdout_link(
                        block.stdin
                    )  # link previous blocks stdout with current blocks stdin
                else:
                    raise Exception("run step requires input but has no upstream")

    @staticmethod
    async def terminate(self) -> bool:
        return False


async def experimental_run(  # noqa: WPS217
    elb: ExtractLoadBlocks, project_settings_service: ProjectSettingsService
):
    """
    This is very much still a WIP. If you're getting an early look at this MR keep in mind this isn't the final state.
    """
    stream_buffer_size = project_settings_service.get("elt.buffer_size")
    line_length_limit = stream_buffer_size // 2

    output_exception_future = asyncio.ensure_future(
        asyncio.wait(
            [*elb.stdout_futures, *elb.stdout_futures],
            return_when=asyncio.FIRST_EXCEPTION,
        )
    )

    done = await elb.process_wait(output_exception_future)

    output_futures_failed = first_failed_future(output_exception_future, done)
    if output_futures_failed:
        # Special behavior for the producer stdout handler raising a line length limit error.
        if elb.head.proxy_stdout() == output_futures_failed:
            handle_producer_line_length_limit_error(
                output_futures_failed.exception(),
                line_length_limit=line_length_limit,
                stream_buffer_size=stream_buffer_size,
            )
        raise output_futures_failed.pop().exception()
    else:
        # If all of the output handlers completed without raising an exception,
        # we still need to wait for all of the underlying block processes to complete.
        done, _ = await asyncio.wait(
            [*elb.process_futures],
            return_when=asyncio.FIRST_COMPLETED,
        )

    producer = elb.head
    consumer = elb.tail

    if consumer.process_future.done():
        consumer_code = consumer.process_future.result()

        # TODO: when introducing inline transformers, we'll need to switch to upstream_complete(index) to verify
        # everything upstream completed.
        if elb.upstream_complete(len(elb.blocks) - 1):
            producer_code = producer.process_future.result()
        else:
            # If the consumer (target) completes before the upstream producers, it failed before processing all output
            # So we should kill the upstream producers and cancel output processing since theres no final destination
            # to forward output to.

            # TODO: when introducing inline transformers, we'll need to switch to upstream_stop() to stop
            # everything upstream. I haven't done that yet to keep the door open for a refactor when add stream maps.

            await producer.stop()
            # Pretend the producer (tap) finished successfully since it didn't itself fail
            producer_code = 0

        # Wait for all buffered consumer (target) output to be processed
        await asyncio.wait([consumer.proxy_stdout(), consumer.proxy_stderr()])

    elif producer.process_future.done():
        producer_code = producer.process_future.result()

        # If the tap completes before the target, the target should have a chance to process all tap output
        # Wait for all buffered tap output to be processed
        await asyncio.wait([producer.proxy_stdout(), producer.proxy_stderr()])

        # Close target stdin so process can complete naturally
        consumer.stdin.close()
        with suppress(AttributeError):  # `wait_closed` is Python 3.7+
            await consumer.stdin.wait_closed()

        # Wait for all buffered target output to be processed
        await asyncio.wait([consumer.proxy_stdout(), consumer.proxy_stderr()])

        # Wait for target to complete
        consumer_code = await consumer.process_future
    else:  # would imply that a (not yet implemented) inline transformer finished first
        await producer.stop()
        producer_code = 1
        await consumer.stop()
        consumer_code = 1
        raise RunnerError(
            "Unexpected future in ExtractLoadBlock. Assume extractor and loader failed",
            {PluginType.EXTRACTORS: producer_code, PluginType.LOADERS: consumer_code},
        )

    if producer_code and consumer_code:
        raise RunnerError(
            "Extractor and loader failed",
            {PluginType.EXTRACTORS: producer_code, PluginType.LOADERS: consumer_code},
        )
    elif producer_code:
        raise RunnerError("Extractor failed", {PluginType.EXTRACTORS: producer_code})
    elif consumer_code:
        raise RunnerError("Loader failed", {PluginType.LOADERS: consumer_code})
