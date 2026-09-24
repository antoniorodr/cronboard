from cronboard.services.cron_dir_entry import CronDirEntry


async def test_is_dir() -> None:
    crondir_entry = CronDirEntry("test", "/test", True)
    assert crondir_entry.is_dir()


async def test_is_file() -> None:
    crondir_entry = CronDirEntry("test", "/test", False)
    assert not crondir_entry.is_dir()
