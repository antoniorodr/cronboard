import pytest
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation


@pytest.mark.asyncio
async def test_open_delete_cronjob_modal(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        assert isinstance(app.screen, CronDeleteConfirmation)


@pytest.mark.asyncio
async def test_delete_cronjob_cancel(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        await pilot.press("tab")
        await pilot.press("enter")
        assert not isinstance(app.screen, CronDeleteConfirmation)


@pytest.mark.asyncio
async def test_delete_cronjob_confirm(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
