import pytest
from cronboard.app import CronBoard


@pytest.fixture
def app():
    return CronBoard()
