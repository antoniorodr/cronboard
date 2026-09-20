from cronboard.widgets.cron_table import CronTable


async def test_if_cronjob_exists(create_cronjob):
    app, (identificator, cmd) = create_cronjob
    crontable = app.query_one("#local-crontable")
    assert crontable.find_if_cronjob_exists(identificator, cmd) is not None
