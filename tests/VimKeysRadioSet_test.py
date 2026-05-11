import pytest
from textual.app import App, ComposeResult
from textual.widgets import RadioButton

from cronboard.app import CronBoard
from cronboard_widgets.VimKeysRadioSet import VimKeysRadioSet
from cronboard_widgets.CronCreator import CronCreator


class _RadioDemoApp(App[None]):
    def compose(self) -> ComposeResult:
        yield VimKeysRadioSet(
            RadioButton("A", id="a"),
            RadioButton("B", id="b"),
        )


@pytest.mark.asyncio
async def test_vim_keys_radio_set_jk_cycles_selection():
    async with _RadioDemoApp().run_test() as pilot:
        radio = pilot.app.query_one(VimKeysRadioSet)
        pilot.app.set_focus(radio)
        assert radio.pressed_button is not None
        start_id = radio.pressed_button.id
        await pilot.press("j")
        assert radio.pressed_button.id != start_id
        await pilot.press("k")
        assert radio.pressed_button.id == start_id


@pytest.mark.asyncio
async def test_cron_creator_radio_responds_to_jk(app: CronBoard):
    async with app.run_test() as pilot:
        await pilot.press("c")
        assert isinstance(pilot.app.screen, CronCreator)
        radio = pilot.app.screen.query_one(VimKeysRadioSet)
        radio.focus()
        before = radio.pressed_button.id if radio.pressed_button else None
        await pilot.press("j")
        after_j = radio.pressed_button.id if radio.pressed_button else None
        assert after_j != before
        await pilot.press("k")
        assert radio.pressed_button.id == before
