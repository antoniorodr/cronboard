import types

import pytest

from cronboard.app import CronBoard


@pytest.fixture
def app() -> types.GeneratorType:
    cronboard_app: CronBoard = CronBoard()
    yield cronboard_app
