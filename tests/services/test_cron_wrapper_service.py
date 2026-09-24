from cronboard.services.cron_wrapper_service import CronWrapperService


async def test_remote_bash_path(generate_ssh_client) -> None:
    assert CronWrapperService.get_remote_bash_path(generate_ssh_client) == "/bin/bash"
    generate_ssh_client.close()


async def test_is_wrapper_installed_remote(generate_ssh_client) -> None:
    assert CronWrapperService.is_wrapper_installed_remote(generate_ssh_client) == False
    generate_ssh_client.close()


async def test_wrap_command_local() -> None:
    result: str = CronWrapperService.wrap_command("test", "test", None)
    assert "cron-wrapper.sh" in result
    assert "cronboard1:" in result
