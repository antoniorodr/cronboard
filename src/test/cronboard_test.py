from cronboard.app import CronBoard
import pytest


@pytest.mark.asyncio
async def test_change_tab():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        assert app.local_table.has_focus
