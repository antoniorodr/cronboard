import pytest
from cronboard.app import CronBoard
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronCreator import CronAutoComplete


@pytest.fixture
def app():
    return CronBoard()


@pytest.fixture
def autocomplete():
    return CronAutoComplete.__new__(CronAutoComplete)


def make_creator(mocker, **kwargs):
    cron = mocker.MagicMock()
    cron.__iter__ = mocker.MagicMock(return_value=iter([]))
    return CronCreator(cron, **kwargs)
