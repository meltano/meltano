from __future__ import annotations

from unittest import mock

import click
import pytest
import structlog
from sqlalchemy.orm import Session

from meltano.core.block.block_parser import BlockParser, is_command_block
from meltano.core.block.blockset import BlockSetValidationError
from meltano.core.task_sets import TaskSets


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


class TestBlockParserSelectFilters:
    @pytest.fixture
    def logger(self) -> structlog.BoundLogger:
        return structlog.getLogger("test")

    def test_select_filter_applies_to_the_named_extractor(
        self,
        project,
        logger,
        tap,
        target,
    ) -> None:
        parser = BlockParser(
            logger,
            project,
            [tap.name, target.name],
            select_filters={tap.name: ["tags", "!commits"]},
        )
        try:
            (elb,) = parser.find_blocks(0)
            extractor, loader = elb.blocks[0], elb.blocks[-1]

            assert extractor.context.settings_service.get("_select_filter") == [
                "tags",
                "!commits",
            ]
            assert (
                "_select_filter" not in loader.context.settings_service.config_override
            )
        finally:
            parser.close_sessions()

    def test_no_select_filter_leaves_the_extra_alone(
        self,
        project,
        logger,
        tap,
        target,
    ) -> None:
        parser = BlockParser(logger, project, [tap.name, target.name])
        try:
            (elb,) = parser.find_blocks(0)
            settings = elb.blocks[0].context.settings_service
            assert "_select_filter" not in settings.config_override
        finally:
            parser.close_sessions()

    def test_select_filter_replaces_the_configured_extra(
        self,
        project,
        logger,
        tap,
        target,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("TAP_MOCK__SELECT_FILTER", '["configured"]')
        for select_filters, expected in (
            (None, ["configured"]),
            ({tap.name: ["tags"]}, ["tags"]),
        ):
            parser = BlockParser(
                logger,
                project,
                [tap.name, target.name],
                select_filters=select_filters,
            )
            try:
                (elb,) = parser.find_blocks(0)
                settings = elb.blocks[0].context.settings_service
                assert settings.get("_select_filter") == expected
            finally:
                parser.close_sessions()

    def test_select_filter_applies_each_time_the_extractor_runs(
        self,
        project,
        logger,
        tap,
        target,
    ) -> None:
        parser = BlockParser(
            logger,
            project,
            [tap.name, target.name, tap.name, target.name],
            select_filters={tap.name: ["tags"]},
        )
        try:
            elbs = list(parser.find_blocks(0))
            assert len(elbs) == 2
            for elb in elbs:
                settings = elb.blocks[0].context.settings_service
                assert settings.get("_select_filter") == ["tags"]
        finally:
            parser.close_sessions()

    def test_select_filter_for_an_extractor_in_a_job(
        self,
        project,
        logger,
        tap,
        target,
        task_sets_service,
    ) -> None:
        task_sets_service.add(
            TaskSets("select-filter-job", [f"{tap.name} {target.name}"])
        )
        try:
            parser = BlockParser(
                logger,
                project,
                ["select-filter-job"],
                select_filters={tap.name: ["tags"]},
            )
            try:
                (elb,) = parser.find_blocks(0)
                settings = elb.blocks[0].context.settings_service
                assert settings.get("_select_filter") == ["tags"]
            finally:
                parser.close_sessions()
        finally:
            task_sets_service.remove("select-filter-job")

    def test_select_filter_names_every_unknown_plugin(
        self,
        project,
        logger,
        tap,
        target,
    ) -> None:
        with pytest.raises(
            click.ClickException,
            match=f"'tap-elsewhere', '{target.name}', which are not extractors",
        ):
            BlockParser(
                logger,
                project,
                [tap.name, target.name],
                select_filters={"tap-elsewhere": ["a"], target.name: ["b"]},
            )

    @pytest.mark.parametrize("named", ("target", "tap-elsewhere"))
    def test_select_filter_must_name_an_extractor_in_the_run(
        self,
        project,
        logger,
        tap,
        target,
        named: str,
    ) -> None:
        name = target.name if named == "target" else named
        with pytest.raises(click.ClickException, match=f"'{name}'.*not an extractor"):
            BlockParser(
                logger,
                project,
                [tap.name, target.name],
                select_filters={name: ["tags"]},
            )
