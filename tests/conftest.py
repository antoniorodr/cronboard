import pytest
import pytest_asyncio
from cronboard.app import CronBoard
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronCreator import CronAutoComplete


@pytest.fixture
def app(mocker):
    fake_job = mocker.MagicMock()
    fake_job.comment = "test-job"
    fake_job.command = "echo hello"
    fake_job.render.return_value = "* * * * * echo hello"

    fake_cron = mocker.MagicMock()
    fake_cron.__iter__ = mocker.MagicMock(side_effect=lambda: iter([fake_job]))
    mocker.patch("cronboard_widgets.CronTable.CronTab", return_value=fake_cron)
    mocker.patch(
        "cronboard_widgets.CronDeleteConfirmation.CronTab", return_value=fake_cron
    )
    yield CronBoard()


@pytest.fixture
def autocomplete():
    yield CronAutoComplete.__new__(CronAutoComplete)


@pytest_asyncio.fixture
async def pilot(app):
    async with app.run_test() as pilot_impl:
        yield pilot_impl


def make_creator(mocker, **kwargs):
    cron = mocker.MagicMock()
    cron.__iter__ = mocker.MagicMock(return_value=iter([]))
    return CronCreator(cron, **kwargs)
