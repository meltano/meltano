"""Test BlockParser job environment variable functionality."""

from __future__ import annotations

import pytest
import structlog

from meltano.core.block.block_parser import BlockParser
from meltano.core.task_sets import TaskSets


class TestBlockParserJobEnv:
    @pytest.mark.usefixtures("project", "session")
    def test_job_env_tracking_during_expansion(
        self,
        project,
        task_sets_service,
        utility,
    ) -> None:
        """Test that BlockParser correctly tracks job env during expansion."""
        # Create a job with environment variables
        job_env = {"TEST_JOB_VAR": "test_value", "ANOTHER_VAR": "another_value"}
        job = TaskSets(
            name="env_tracking_job",
            tasks=[utility.name],
            env=job_env,
        )
        task_sets_service.add(job)

        # Create BlockParser and verify job env tracking
        logger = structlog.get_logger(__name__)
        parser = BlockParser(logger, project, ["env_tracking_job"])

        # Verify job expansion worked
        assert len(parser._plugins) == 1
        assert parser._plugins[0].name == utility.name

        # Verify job env was tracked for the expanded block
        assert 0 in parser._job_envs
        assert parser._job_envs[0] == job_env

    @pytest.mark.usefixtures("project", "session")
    def test_mixed_jobs_and_direct_plugins(
        self,
        project,
        task_sets_service,
        utility,
    ) -> None:
        """Test job env tracking with mix of jobs and direct plugins."""
        job_env = {"MIXED_JOB_VAR": "mixed_value"}
        job = TaskSets(
            name="mixed_test_job",
            tasks=[utility.name],
            env=job_env,
        )
        task_sets_service.add(job)

        # Mix: direct plugin, then job
        logger = structlog.get_logger(__name__)
        parser = BlockParser(logger, project, [utility.name, "mixed_test_job"])

        # Should have 2 plugins: direct utility + job's utility
        assert len(parser._plugins) == 2

        # Verify env tracking
        assert parser._job_envs[0] == {}  # Direct plugin (no job env)
        assert parser._job_envs[1] == job_env  # Job's plugin gets job env

    @pytest.mark.usefixtures("project", "session")
    def test_job_env_context_in_plugin_command_block(
        self,
        project,
        task_sets_service,
        utility,
    ) -> None:
        """Test that job env reaches PluginCommandBlock context."""
        job_env = {"BLOCK_CONTEXT_VAR": "block_context_value"}
        job = TaskSets(
            name="context_test_job",
            tasks=[utility.name],
            env=job_env,
        )
        task_sets_service.add(job)

        # Create BlockParser and get blocks
        logger = structlog.get_logger(__name__)
        parser = BlockParser(logger, project, ["context_test_job"])
        parsed_blocks = list(parser.find_blocks(0))

        assert len(parsed_blocks) == 1

        # Verify the block has job env in its context
        block = parsed_blocks[0]
        assert hasattr(block, "context")
        assert hasattr(block.context, "job_env")
        assert block.context.job_env == job_env

    @pytest.mark.usefixtures("project", "session")
    def test_job_env_with_extract_load_blocks(
        self,
        project,
        task_sets_service,
        tap,
        target,
    ) -> None:
        """Test that job env works with ExtractLoadBlocks (tap + target)."""
        job_env = {"ELB_JOB_VAR": "elb_value"}
        job = TaskSets(
            name="elb_test_job",
            tasks=[f"{tap.name} {target.name}"],
            env=job_env,
        )
        task_sets_service.add(job)

        # Create BlockParser and get blocks
        logger = structlog.get_logger(__name__)
        parser = BlockParser(logger, project, ["elb_test_job"])
        parsed_blocks = list(parser.find_blocks(0))

        assert len(parsed_blocks) == 1

        # Should be an ExtractLoadBlocks with job env in context
        elb_block = parsed_blocks[0]
        assert hasattr(elb_block, "context")
        assert hasattr(elb_block.context, "job_env")
        assert elb_block.context.job_env == job_env
