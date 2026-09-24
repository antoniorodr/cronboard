from cronboard.services.config_service import ConfigService


async def test_save_job_settings():
    server_name = "local"
    cron_name = "test"
    notifications = True
    logging = True
    assert ConfigService.save_job_settings(
        server_name, cron_name, notifications, logging
    )
