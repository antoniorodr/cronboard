import pytest
from cronboard.app import CronBoard
from textual.widgets import Tree

@pytest.mark.asyncio
async def test_change_tab(app: CronBoard):
    async with app.run_test() as pilot:
        assert app.tabs.active == "local"

        await pilot.press("tab")
        await pilot.pause()

        assert app.tabs.active == "servers"
        assert app.servers is not None

        server_tree = app.servers.query_one("#servers-tree", Tree)
        assert server_tree.has_focus

@pytest.mark.asyncio
async def test_refresh_data(app: CronBoard):
    async with app.run_test() as pilot:
        initial_data = app.local_table
        await pilot.press("r")
        refreshed_data = app.local_table
        assert initial_data == refreshed_data


@pytest.mark.asyncio
async def test_quit_app(app: CronBoard):
    async with app.run_test() as pilot:
        await pilot.press("ctrl+q")
        assert app.is_running is False
