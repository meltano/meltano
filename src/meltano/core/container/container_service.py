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
            docker: Docker session.
            name: Container name.
            env: Environment for the
            pull: Pull image from registry.

        Returns:
            Docker container information after execution.
        """
        async with Docker() as docker:
            if pull:
                await docker.images.pull(spec.image)

            config = spec.get_docker_config(additional_env=env)
            container = await docker.containers.run(config, name=name)

            try:
                async for line in container.log(follow=True, stdout=True):
                    logger.info(line.rstrip())

                await container.wait()
                info = await container.show()
            finally:
                await container.delete(force=True)

        return info
