import pytest
import pytest_asyncio
from cronboard.app import CronBoard
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronCreator import CronAutoComplete


@pytest.fixture
def app():
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
