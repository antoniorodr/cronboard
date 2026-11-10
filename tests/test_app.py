import tomllib

from cronboard.app import CronBoard


async def test_close(app: CronBoard) -> None:
    async with app.run_test() as pilot:
        await pilot.press("q")
    assert pilot.app.return_code == 0


async def test_load_config(app: CronBoard) -> None:
    async with app.run_test() as pilot:
        if app.config_path.exists():
            assert pilot.app.theme == app.theme


def test_get_version(app: CronBoard) -> None:
    with open("pyproject.toml", "rb") as f:
        version = tomllib.load(f)["project"]["version"]
    assert app.get_version() == version
