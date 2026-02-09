from cronboard.app import CronBoard
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation
from cronboard_widgets.CronSSHModal import CronSSHModal
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


def test_parse_host_info_defaults_port():
    hostname, port = CronSSHModal._parse_host_info("node9")
    assert hostname == "node9"
    assert port == 22


def test_parse_host_info_with_port():
    hostname, port = CronSSHModal._parse_host_info("node9:2222")
    assert hostname == "node9"
    assert port == 2222


@pytest.mark.parametrize(
    "value",
    ["", ":", "node9:", ":2222", "node9:abc", "node9:0", "node9:70000"],
)
def test_parse_host_info_invalid(value):
    with pytest.raises(ValueError):
        CronSSHModal._parse_host_info(value)
