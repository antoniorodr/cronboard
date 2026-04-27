import pytest
from pytest_mock import MockerFixture
from rich.text import Text
from cronboard_widgets.CronTable import CronTable


def make_table(mocker: MockerFixture, rows=None, row_count=0):
    """Create a CronTable instance with pre-populated _rows_data."""
    table = CronTable.__new__(CronTable)
    table._rows_data = rows or []
    table._search_matches = []
    table._search_index = -1
    table._search_query = ""
    mocker.patch.object(type(table), 'row_count', new_callable=lambda: property(lambda self: row_count))
    return table


# ---------------------------------------------------------------------------
# check_action
# ---------------------------------------------------------------------------


def test_check_action_returns_false_for_navigation_when_empty(mocker: MockerFixture):
    table = make_table(mocker, row_count=0)
    for action in ("cron_search", "edit_cronjob", "delete_cronjob", "pause_cronjob"):
        assert table.check_action(action, ()) is False


def test_check_action_returns_true_for_navigation_when_not_empty(mocker: MockerFixture):
    table = make_table(mocker, row_count=3)
    for action in ("cron_search", "edit_cronjob", "delete_cronjob", "pause_cronjob"):
        assert table.check_action(action, ()) is True


def test_check_action_always_returns_true_for_create(mocker: MockerFixture):
    table = make_table(mocker, row_count=0)
    assert table.check_action("create_cronjob_keybind", ()) is True


# ---------------------------------------------------------------------------
# _highlight_text
# ---------------------------------------------------------------------------


def test_highlight_text_returns_rich_text(mocker: MockerFixture):
    table = make_table(mocker)
    result = table._highlight_text("echo hello", "hello")
    assert isinstance(result, Text)
    assert "hello" in str(result)


def test_highlight_text_case_insensitive(mocker: MockerFixture):
    table = make_table(mocker)
    result = table._highlight_text("Echo Hello", "echo")
    assert isinstance(result, Text)


def test_highlight_text_no_match_returns_plain_text(mocker: MockerFixture):
    table = make_table(mocker)
    result = table._highlight_text("echo hello", "python")
    assert isinstance(result, Text)
    assert str(result) == "echo hello"


# ---------------------------------------------------------------------------
# apply_search
# ---------------------------------------------------------------------------


def test_apply_search_finds_match_in_command(mocker: MockerFixture):
    rows = [
        ("backup", "* * * * *", "echo hello", "01.01.2024 at 00:00", "01.01.2024 at 00:01", "Active"),
        ("other", "0 * * * *", "python3 script.py", "01.01.2024 at 00:00", "01.01.2024 at 01:00", "Active"),
    ]
    table = make_table(mocker, rows)
    table._highlight_matches = mocker.Mock()
    table.move_cursor = mocker.Mock()
    table.notify = mocker.Mock()
    table._restore_cells = mocker.Mock()

    table.apply_search("echo")

    assert 0 in table._search_matches
    assert 1 not in table._search_matches
    table.notify.assert_called_once()


def test_apply_search_empty_query_restores_cells(mocker: MockerFixture):
    table = make_table(mocker)
    table._restore_cells = mocker.Mock()
    table.notify = mocker.Mock()

    table.apply_search("")

    table._restore_cells.assert_called_once()
    assert table._search_query == ""


def test_apply_search_no_match_notifies(mocker: MockerFixture):
    rows = [("job", "* * * * *", "echo hello", "", "", "Active")]
    table = make_table(mocker, rows)
    table._restore_cells = mocker.Mock()
    table.notify = mocker.Mock()

    table.apply_search("python")

    assert table._search_matches == []
    assert table._search_index == -1
    table.notify.assert_called_once()


def test_apply_search_finds_match_in_identifier(mocker: MockerFixture):
    rows = [
        ("backup-job", "* * * * *", "echo hello", "", "", "Active"),
        ("other-job", "0 * * * *", "python3 run.py", "", "", "Active"),
    ]
    table = make_table(mocker, rows)
    table._highlight_matches = mocker.Mock()
    table.move_cursor = mocker.Mock()
    table.notify = mocker.Mock()
    table._restore_cells = mocker.Mock()

    table.apply_search("backup")

    assert 0 in table._search_matches
    assert 1 not in table._search_matches


# ---------------------------------------------------------------------------
# action_clear_search
# ---------------------------------------------------------------------------


def test_action_clear_search_resets_state(mocker: MockerFixture):
    table = make_table(mocker)
    table._search_query = "test"
    table._search_matches = [0, 1]
    table._search_index = 1
    table._restore_cells = mocker.Mock()

    table.action_clear_search()

    assert table._search_query == ""
    assert table._search_matches == []
    assert table._search_index == -1
    table._restore_cells.assert_called_once()


# ---------------------------------------------------------------------------
# action_search_next / action_search_prev
# ---------------------------------------------------------------------------


def test_action_search_next_cycles_forward(mocker: MockerFixture):
    table = make_table(mocker)
    table._search_matches = [0, 2, 5]
    table._search_index = 0
    table.move_cursor = mocker.Mock()

    table.action_search_next()

    assert table._search_index == 1
    table.move_cursor.assert_called_once_with(row=2)


def test_action_search_next_wraps_around(mocker: MockerFixture):
    table = make_table(mocker)
    table._search_matches = [0, 2, 5]
    table._search_index = 2
    table.move_cursor = mocker.Mock()

    table.action_search_next()

    assert table._search_index == 0
    table.move_cursor.assert_called_once_with(row=0)


def test_action_search_next_no_op_when_no_matches(mocker: MockerFixture):
    table = make_table(mocker)
    table._search_matches = []
    table.move_cursor = mocker.Mock()

    table.action_search_next()

    table.move_cursor.assert_not_called()


def test_action_search_prev_cycles_backward(mocker: MockerFixture):
    table = make_table(mocker)
    table._search_matches = [0, 2, 5]
    table._search_index = 2
    table.move_cursor = mocker.Mock()

    table.action_search_prev()

    assert table._search_index == 1
    table.move_cursor.assert_called_once_with(row=2)


def test_action_search_prev_wraps_around(mocker: MockerFixture):
    table = make_table(mocker)
    table._search_matches = [0, 2, 5]
    table._search_index = 0
    table.move_cursor = mocker.Mock()

    table.action_search_prev()

    assert table._search_index == 2
    table.move_cursor.assert_called_once_with(row=5)


def test_action_search_prev_no_op_when_no_matches(mocker: MockerFixture):
    table = make_table(mocker)
    table._search_matches = []
    table.move_cursor = mocker.Mock()

    table.action_search_prev()

    table.move_cursor.assert_not_called()
