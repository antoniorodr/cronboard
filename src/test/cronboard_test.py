from cronboard.app import CronBoard
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation
import pytest


@pytest.mark.asyncio
async def test_change_tab():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        assert app.local_table.has_focus


@pytest.mark.asyncio
async def test_refresh_data():
    app = CronBoard()
    async with app.run_test() as pilot:
        initial_data = app.local_table
        await pilot.press("r")
        refreshed_data = app.local_table
        assert initial_data == refreshed_data


@pytest.mark.asyncio
async def test_quit_app():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("ctrl+q")
        assert app.is_running is False


@pytest.mark.asyncio
async def test_create_cronjob():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("c")
        assert isinstance(app.screen, CronCreator)


@pytest.mark.asyncio
async def test_delete_cronjob():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        assert isinstance(app.screen, CronDeleteConfirmation)
