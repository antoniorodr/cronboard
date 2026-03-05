import pytest


@pytest.mark.asyncio
async def test_change_tab(app):
    async with app.run_test() as pilot:
        await pilot.press("tab")
        assert app.local_table.has_focus


@pytest.mark.asyncio
async def test_refresh_data(app):
    async with app.run_test() as pilot:
        initial_data = app.local_table
        await pilot.press("r")
        refreshed_data = app.local_table
        assert initial_data == refreshed_data


@pytest.mark.asyncio
async def test_quit_app(app):
    async with app.run_test() as pilot:
        await pilot.press("ctrl+q")
        assert app.is_running is False
