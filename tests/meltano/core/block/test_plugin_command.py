import pytest
from asynctest import CoroutineMock, Mock

from meltano.core.block.plugin_command import plugin_command_invoker


@pytest.fixture()
def dbt_process():
    dbt = Mock()
    dbt.name = "dbt"
    dbt.wait = CoroutineMock(return_value=0)

    dbt.stdout.readline = CoroutineMock(return_value="{}")  # noqa: P103
    dbt.wait = CoroutineMock(return_value=0)
    return dbt


@pytest.mark.asyncio
async def test_run_passes_command_args_when_required(
    project, session, project_plugins_service, dbt, dbt_process
):
    cmd = plugin_command_invoker(
        dbt,
        project,
        command="test",
    )

    start_mock = CoroutineMock()
    cmd.start = start_mock

    await cmd._start()
    assert not cmd.start.call_args[0]

    cmd = plugin_command_invoker(
        dbt,
        project,
        command="test",
        command_args=["--foo", "--bar"],
    )

    start_mock = CoroutineMock()
    cmd.start = start_mock

    await cmd._start()
    assert len(cmd.start.call_args[0]) == 1
    assert cmd.start.call_args[0][0] == ["--foo", "--bar"]
