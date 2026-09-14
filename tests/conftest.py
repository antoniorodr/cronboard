import types

import pytest

from cronboard.app import CronBoard


@pytest.fixture
async def app() -> types.AsyncGeneratorType:
    cronboard_app: CronBoard = CronBoard()
    yield cronboard_app
