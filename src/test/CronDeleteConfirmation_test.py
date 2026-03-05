import pytest
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation


@pytest.mark.asyncio
async def test_delete_cronjob(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        assert isinstance(app.screen, CronDeleteConfirmation)
