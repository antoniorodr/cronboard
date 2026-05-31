from rich.text import Text

from cronboard.widgets.CronTable import CronTable


def test_check_action_blocks_row_actions_when_table_is_empty():
    table = CronTable()

    assert table.check_action("cron_search", ()) is False
    assert table.check_action("edit_cronjob", ()) is False
    assert table.check_action("delete_cronjob", ()) is False
    assert table.check_action("refresh", ()) is True


def test_apply_search_tracks_matches_case_insensitively(mocker):
    table = CronTable()
    table._rows_data = [
        ("nightly-backup", "0 0 * * *", "python backup.py", "False", "", "", Text()),
        ("healthcheck", "*/5 * * * *", "curl http://example", "False", "", "", Text()),
    ]
    highlight = mocker.patch.object(table, "_highlight_matches")
    move_cursor = mocker.patch.object(table, "move_cursor")
    notify = mocker.patch.object(table, "notify")

    table.apply_search("BACKUP")

    assert table._search_query == "backup"
    assert table._search_matches == [0]
    assert table._search_index == 0
    highlight.assert_called_once_with()
    move_cursor.assert_called_once_with(row=0)
    notify.assert_called_once_with("1 match(es) for 'backup'")


def test_apply_search_restores_rows_for_empty_query(mocker):
    table = CronTable()
    table._rows_data = [
        ("nightly-backup", "0 0 * * *", "python backup.py", "False", "", "", Text())
    ]
    restore_cells = mocker.patch.object(table, "_restore_cells")

    table.apply_search("")

    assert table._search_query == ""
    assert table._search_matches == []
    restore_cells.assert_called_once_with()


def test_apply_search_reports_no_matches(mocker):
    table = CronTable()
    table._rows_data = [
        ("nightly-backup", "0 0 * * *", "python backup.py", "False", "", "", Text())
    ]
    notify = mocker.patch.object(table, "notify")

    table.apply_search("deploy")

    assert table._search_matches == []
    assert table._search_index == -1
    notify.assert_called_once_with("No matches for 'deploy'")


def test_find_if_cronjob_exists_matches_wrapped_command_variant(mocker):
    table = CronTable()
    job = mocker.Mock(comment="nightly-backup", command="wrapped-command")
    table.cron = [job]
    mocker.patch(
        "cronboard.widgets.CronTable.wrap_command",
        return_value="wrapped-command",
    )
    mocker.patch(
        "cronboard.widgets.CronTable.command_without_wrapper",
        return_value="backup.py",
    )

    result = table.find_if_cronjob_exists("nightly-backup", "backup.py")

    assert result is job


def test_find_if_cronjob_exists_matches_unwrapped_command_variant(mocker):
    table = CronTable()
    job = mocker.Mock(comment="nightly-backup", command="backup.py")
    table.cron = [job]
    mocker.patch(
        "cronboard.widgets.CronTable.wrap_command",
        return_value="wrapped-command",
    )
    mocker.patch(
        "cronboard.widgets.CronTable.command_without_wrapper",
        return_value="backup.py",
    )

    result = table.find_if_cronjob_exists("nightly-backup", "wrapped-command")

    assert result is job
