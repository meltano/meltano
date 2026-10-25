from __future__ import annotations

from unittest import mock

import pytest
import structlog
from sqlalchemy.orm import Session

from meltano.core.block.block_parser import BlockParser, is_command_block
from meltano.core.block.blockset import BlockSetValidationError


class TestParserUtils:
    def test_is_command_block(self, tap, dbt) -> None:
        assert not is_command_block(tap)
        assert is_command_block(dbt)


class TestBlockParserSessions:
    @pytest.fixture
    def logger(self) -> structlog.BoundLogger:
        return structlog.getLogger("test")

    @pytest.mark.usefixtures("tap", "target")
    def test_close_sessions_extract_load(self, project, logger, tap, target) -> None:
        parser = BlockParser(logger, project, [tap.name, target.name])
        with mock.patch.object(Session, "close", autospec=True) as close:
            assert len(list(parser.find_blocks(0))) == 1
            close.assert_not_called()

            parser.close_sessions()
            assert close.call_count == 1

            # Sessions are only closed once
            parser.close_sessions()
            assert close.call_count == 1

    @pytest.mark.usefixtures("dbt")
    def test_close_sessions_plugin_command(self, project, logger) -> None:
        parser = BlockParser(logger, project, ["dbt:run"])
        with mock.patch.object(Session, "close", autospec=True) as close:
            assert len(list(parser.find_blocks(0))) == 1
            close.assert_not_called()

            parser.close_sessions()
            # The command's own session, and that of the extract-load context
            # builder that was created while looking for an extract-load set
            assert close.call_count == 2

    @pytest.mark.usefixtures("tap", "target")
    def test_close_sessions_after_parse_error(
        self,
        project,
        logger,
        tap,
        target,
    ) -> None:
        # The second extractor has no loader, so parsing fails after the first
        # extract-load set was built
        parser = BlockParser(logger, project, [tap.name, target.name, tap.name])
        with mock.patch.object(Session, "close", autospec=True) as close:
            with pytest.raises(BlockSetValidationError):
                list(parser.find_blocks(0))

            close.assert_not_called()

            parser.close_sessions()
            # One session per extract-load set, including the incomplete one
            assert close.call_count == 2
