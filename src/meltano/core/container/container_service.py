"""Container management."""

from __future__ import annotations

from aiodocker import Docker
from structlog.stdlib import get_logger

from .container_spec import ContainerSpec

logger = get_logger(__name__)


class ContainerService:
    """[summary]."""

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
        async with Docker() as docker:
            if pull:
                await docker.images.pull(spec.image)

            config = spec.get_docker_config(additional_env=env)
            container = await docker.containers.run(config, name=name)

            async for line in container.log(follow=True, stdout=True, stderr=True):
                logger.info(line.rstrip())

            try:
                await container.wait()
            except Exception as exc:
                logger.exception("Container run failed", exc_info=exc)
            finally:
                info = await container.show()
                await container.delete(force=True)

        return info
