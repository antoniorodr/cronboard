import pytest
from pytest_mock import MockerFixture
from textual.app import App, ComposeResult

from cronboard.widgets.LogView import LogView
from textual.widgets import ListView, Log


_LOG_VIEW = "cronboard.widgets.LogView"


class LogViewHarnessApp(App):
    def disable_tab(self) -> None:
        pass

    def compose(self) -> ComposeResult:
        yield LogView(identificator="test-job")


@pytest.fixture
def log_paths_two(mocker: MockerFixture):
    return mocker.patch(
        f"{_LOG_VIEW}.get_log_files",
        return_value={
            "log_a": "/logs/a.log",
            "log_b": "/logs/b.log",
        },
    )


@pytest.fixture
def read_log_mock(mocker: MockerFixture):
    return mocker.patch(
        f"{_LOG_VIEW}.read_log_file",
        side_effect=lambda path, _ssh: [f"CONTENT:{path}\n"],
    )


def test_check_action_disables_cursor_bindings_when_no_logs(mocker: MockerFixture):
    mocker.patch(f"{_LOG_VIEW}.get_log_files", return_value={})
    view = LogView(identificator="job")

    assert view.check_action("cursor_down", ()) is False
    assert view.check_action("cursor_up", ()) is False
    assert view.check_action("cursor_left", ()) is False
    assert view.check_action("cursor_right", ()) is False


def test_check_action_enables_cursor_bindings_when_logs_exist(mocker: MockerFixture):
    mocker.patch(
        f"{_LOG_VIEW}.get_log_files",
        return_value={"one": "/logs/one.log"},
    )
    view = LogView(identificator="job")

    assert view.check_action("cursor_down", ()) is True
    assert view.check_action("cursor_up", ()) is True
    assert view.check_action("cursor_left", ()) is True
    assert view.check_action("cursor_right", ()) is True


@pytest.mark.asyncio
async def test_highlight_then_j_loads_second_log(
    log_paths_two,
    read_log_mock,
):
    async with LogViewHarnessApp().run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        pilot.app.query_one(ListView).focus()
        await pilot.pause()

        paths = [c.args[0] for c in read_log_mock.call_args_list]
        assert "/logs/a.log" in paths

        await pilot.press("j")
        await pilot.pause()

        assert read_log_mock.call_args_list[-1].args[0] == "/logs/b.log"


@pytest.mark.asyncio
async def test_k_after_j_loads_first_log_again(
    log_paths_two,
    read_log_mock,
):
    async with LogViewHarnessApp().run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        pilot.app.query_one(ListView).focus()
        await pilot.pause()

        await pilot.press("j")
        await pilot.pause()
        assert read_log_mock.call_args_list[-1].args[0] == "/logs/b.log"

        await pilot.press("k")
        await pilot.pause()
        assert read_log_mock.call_args_list[-1].args[0] == "/logs/a.log"


@pytest.mark.asyncio
async def test_l_focuses_log_j_scrolls_down(
    mocker: MockerFixture,
    log_paths_two,
    read_log_mock,
):
    scroll_mock = mocker.patch.object(Log, "action_scroll_down")

    async with LogViewHarnessApp().run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        pilot.app.query_one(ListView).focus()
        await pilot.pause()

        await pilot.press("l")
        await pilot.pause()

        assert pilot.app.focused is pilot.app.query_one(Log)

        await pilot.press("j")
        await pilot.pause()

        scroll_mock.assert_called_once()


@pytest.mark.asyncio
async def test_h_focuses_list_from_log_pane(
    log_paths_two,
    read_log_mock,
):
    async with LogViewHarnessApp().run_test(size=(100, 40)) as pilot:
        await pilot.pause()
        pilot.app.query_one(ListView).focus()
        await pilot.pause()

        await pilot.press("l")
        await pilot.pause()
        assert pilot.app.focused is pilot.app.query_one(Log)

        await pilot.press("h")
        await pilot.pause()

        assert pilot.app.focused is pilot.app.query_one(ListView)
