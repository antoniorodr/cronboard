import crontab as crontab_module

from cronboard_widgets import CronCommand


def test_get_local_crontab_command_prefers_crontab(mocker):
    mocker.patch(
        "cronboard_widgets.CronCommand.which",
        side_effect=lambda command: f"/usr/bin/{command}"
        if command == "crontab"
        else None,
    )

    assert CronCommand.get_local_crontab_command() == "/usr/bin/crontab"


def test_get_local_crontab_command_uses_fcrontab_when_crontab_missing(mocker):
    mocker.patch(
        "cronboard_widgets.CronCommand.which",
        side_effect=lambda command: f"/usr/bin/{command}"
        if command == "fcrontab"
        else None,
    )

    assert CronCommand.get_local_crontab_command() == "/usr/bin/fcrontab"


def test_create_user_crontab_uses_detected_command_and_restores_default(mocker):
    mocker.patch(
        "cronboard_widgets.CronCommand.get_local_crontab_command",
        return_value="/usr/bin/fcrontab",
    )
    cron_tab = mocker.patch("cronboard_widgets.CronCommand.CronTab")
    original_command = crontab_module.CRON_COMMAND

    CronCommand.create_user_crontab()

    cron_tab.assert_called_once_with(user=True)
    assert crontab_module.CRON_COMMAND == original_command


def test_remote_crontab_list_command_uses_crontab_with_fcrontab_fallback():
    assert CronCommand.remote_crontab_list_command() == (
        "if command -v crontab >/dev/null 2>&1; "
        "then crontab -l; else fcrontab -l; fi"
    )


def test_remote_crontab_write_command_quotes_user():
    assert CronCommand.remote_crontab_write_command("cron user") == (
        "if command -v crontab >/dev/null 2>&1; "
        "then crontab -u 'cron user' -; else fcrontab -u 'cron user' -; fi"
    )
