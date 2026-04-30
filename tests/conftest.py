import pytest
from pytest_mock import MockerFixture
import pytest_asyncio
from cronboard.app import CronBoard
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronCreator import CronAutoComplete
from types import SimpleNamespace
from cronboard_widgets.CronSSHModal import CronSSHModal
from collections.abc import AsyncIterator
from textual.pilot import Pilot


@pytest.fixture
def modal():
    yield CronSSHModal()


@pytest.fixture
def app(mocker: MockerFixture):
    fake_job = mocker.MagicMock()
    fake_job.comment = "test-job"
    fake_job.command = "echo hello"
    fake_job.render.return_value = "* * * * * echo hello"

    fake_cron = mocker.MagicMock()
    fake_cron.__iter__ = mocker.MagicMock(side_effect=lambda: iter([fake_job]))
    mocker.patch("cronboard_widgets.CronTable.CronTab", return_value=fake_cron)
    mocker.patch("cronboard_widgets.CronCommand.CronTab", return_value=fake_cron)
    yield CronBoard()


@pytest.fixture
def autocomplete():
    yield CronAutoComplete.__new__(CronAutoComplete)


@pytest_asyncio.fixture
async def pilot(app: CronBoard) -> AsyncIterator[Pilot]:
    async with app.run_test() as pilot_impl:
        yield pilot_impl


def make_creator(mocker: MockerFixture, **kwargs):
    cron = mocker.MagicMock()
    cron.__iter__ = mocker.MagicMock(return_value=iter([]))
    return CronCreator(cron, **kwargs)


def create_event(button_id: SimpleNamespace):
    event = SimpleNamespace()
    event.button = SimpleNamespace()
    event.button.id = button_id
    return event


def create_job_and_cron(mocker: MockerFixture):
    job = mocker.MagicMock()
    cron = mocker.MagicMock()
    return job, cron


def make_remote_command(mocker: MockerFixture, stderr_output=b"", exit_status=0):

    stdin = mocker.MagicMock()
    stdin.channel.recv_exit_status.return_value = exit_status

    stderr = mocker.MagicMock()
    stderr.read.return_value = stderr_output

    ssh_client = mocker.MagicMock()
    ssh_client.exec_command.return_value = (stdin, mocker.MagicMock(), stderr)
    return stdin, stderr, ssh_client


def make_query_one(mapping):
    def query_one(selector, *_args, **_kwargs):
        return mapping[selector]

    return query_one


def create_content(mocker: MockerFixture):
    return mocker.MagicMock()
