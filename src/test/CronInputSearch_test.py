import pytest
from cronboard_widgets.CronInputSearch import CronInputSearch


@pytest.mark.asyncio
async def test_search_screen(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("/")
        assert isinstance(app.screen, CronInputSearch)
