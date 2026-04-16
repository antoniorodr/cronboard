import pytest
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation
from .conftest import create_event

@pytest.mark.asyncio
async def test_open_delete_cronjob_modal(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        assert isinstance(app.screen, CronDeleteConfirmation)


@pytest.mark.asyncio
async def test_delete_cronjob_cancel(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        await pilot.press("tab")
        await pilot.press("enter")
        assert not isinstance(app.screen, CronDeleteConfirmation)


@pytest.mark.asyncio
async def test_delete_cronjob_confirm(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        await pilot.press("enter")
        assert not isinstance(app.screen, CronDeleteConfirmation)

def create_job_and_cron(mocker):
    job = mocker.MagicMock()
    cron = mocker.MagicMock()
    return job, cron

def make_remote_command(mocker, stderr_output=b"", exit_status=0):

    stdin = mocker.MagicMock()
    stdin.channel.recv_exit_status.return_value = exit_status

    stderr = mocker.MagicMock()
    stderr.read.return_value = stderr_output

    ssh_client = mocker.MagicMock()
    ssh_client.exec_command.return_value = (stdin, mocker.MagicMock(), stderr)
    return stdin, stderr, ssh_client

def test_delete_cronjob_local_write(mocker):
    job, cron = create_job_and_cron(mocker)
    modal = CronDeleteConfirmation(job=job, cron=cron)
    modal.dismiss = mocker.Mock()
    event = create_event("delete")

    modal.on_button_pressed(event)

    cron.remove.assert_called_once_with(job)
    cron.write.assert_called_once_with()
    modal.dismiss.assert_called_once_with(True)


def test_delete_cronjob_remote_write(mocker):
    job, cron = create_job_and_cron(mocker)
    _, _, ssh_client = make_remote_command(mocker)
    modal = CronDeleteConfirmation(
        job=job, cron=cron, remote=True, ssh_client=ssh_client
    )
    modal.dismiss = mocker.Mock()
    modal.write_remote_crontab = mocker.Mock(return_value=True)
    event = create_event("delete")

    modal.on_button_pressed(event)

    cron.remove.assert_called_once_with(job)
    cron.write.assert_not_called()
    modal.write_remote_crontab.assert_called_once_with()
    modal.dismiss.assert_called_once_with(True)


def test_write_remote_crontab(mocker):
    cron, _ = create_job_and_cron(mocker)
    cron.render.return_value = "* * * * * echo hello"
    stdin, stderr, ssh_client = make_remote_command(mocker)
    
    modal = CronDeleteConfirmation(
        cron=cron, remote=True, ssh_client=ssh_client, crontab_user="root"
    )

    result = modal.write_remote_crontab()

    assert result is True
    ssh_client.exec_command.assert_called_once_with("crontab -u root -")
    stdin.write.assert_called_once_with("* * * * * echo hello")
    stdin.channel.shutdown_write.assert_called_once_with()


def test_write_remote_crontab_error(mocker):
    cron, _ = create_job_and_cron(mocker)
    cron.render.return_value = "* * * * * echo hello"
    stdin, stderr, ssh_client = make_remote_command(mocker, stderr_output=b"Error writing crontab", exit_status=1)

    modal = CronDeleteConfirmation(cron=cron, remote=True, ssh_client=ssh_client)

    result = modal.write_remote_crontab()

    assert result is False
    ssh_client.exec_command.assert_called_once_with("crontab -")



