import re

from cronboard.app import CronBoard


async def test_close(app: CronBoard) -> None:
    async with app.run_test() as pilot:
        await pilot.press("q")
        assert pilot.app.exit


async def test_load_config(app: CronBoard) -> None:
    async with app.run_test() as pilot:
        if app.config_path.exists():
            assert pilot.app.theme == app.theme


async def test_get_version(app: CronBoard) -> None:

    def get_version_from_pyproject():
        with open("pyproject.toml", "r") as f:
            content = f.read()
            return (
                match := re.search(r"version = \"(.*)\"", content)
            ) is not None and match.group(1)

    assert app.get_version() == get_version_from_pyproject()
