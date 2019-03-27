def assert_cli_runner(runner, message=None):
    assertion_message = str(message or runner.output)

    assert runner.exit_code == 0, assertion_message
