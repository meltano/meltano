"""Container management."""

from __future__ import annotations

import asyncio
import signal
from typing import TYPE_CHECKING

from structlog.stdlib import get_logger

from meltano.core.container.container_spec import ContainerSpec

if TYPE_CHECKING:
    from aiodocker.containers import DockerContainer


logger = get_logger(__name__)


def stop_container(container: DockerContainer):
    """Stop a Docker container.

    Args:
        container: Running container.
    """
    logger.info("Stopping container", container_id=container.id)
    asyncio.ensure_future(container.stop())


class ContainerService:
    """Wrapper for container interaction."""

    async def run_container(
        self,
        spec: ContainerSpec,
        name: str,
        *,
        env: dict = None,
        pull: bool = False,
    ) -> dict:
        """Run a Docker container.

        Args:
            spec: Command container spec.
            name: Container name.
            env: Environment mapping for the container run.
            pull: Pull image from registry.

        Returns:
            Docker container information after execution.
        """
        import aiodocker

        async with aiodocker.Docker() as docker:
            if pull:
                await docker.images.pull(spec.image)

            config = spec.get_docker_config(additional_env=env)

            logger.info("Running command in container", container_name=name)
            container = await docker.containers.run(config, name=name)
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGINT, lambda: stop_container(container))

            async for line in container.log(follow=True, stdout=True, stderr=True):
                logger.info(line.rstrip())

            try:
                await container.wait()
            except Exception as exc:
                logger.exception("Container run failed", exc_info=exc)
            finally:
                info = await container.show()
                loop.remove_signal_handler(signal.SIGINT)
                await container.delete(force=True)

        return info
