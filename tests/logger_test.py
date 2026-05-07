from pathlib import Path
from pytest_mock import MockerFixture
from cronboard.services.logging.logger import get_log_files, read_log_file

def test_get_log_files_returns_empty_when_dir_missing(
    mocker: MockerFixture,
):
    mock_home = Path("/fake/home")

    mocker.patch(
        "cronboard.services.logging.logger.Path.home",
        return_value=mock_home,
    )

    mocker.patch.object(Path, "exists", return_value=False)

    result = get_log_files("app1", ssh=None)

    assert result == []


def test_get_log_files_returns_dict(mocker: MockerFixture):
    fake_home = Path("/fake/home")

    mocker.patch(
        "cronboard.services.logging.logger.Path.home",
        return_value=fake_home,
    )

    log_dir = fake_home / ".cronboard/logs"

    mocker.patch.object(Path, "exists", return_value=True)

    fake_file1 = Path("/fake/home/.cronboard/logs/app1_log1.log")
    fake_file2 = Path("/fake/home/.cronboard/logs/app1_log2.log")

    mocker.patch.object(
        Path,
        "glob",
        return_value=[fake_file1, fake_file2],
    )

    result = get_log_files("app1", ssh=None)

    assert result == {
        "app1_log1": str(fake_file1),
        "app1_log2": str(fake_file2),
    }


def test_read_log_file_returns_no_logs_when_missing(mocker: MockerFixture):
    mock_file = mocker.patch("cronboard.services.logging.logger.Path")

    fake_path = mocker.Mock()
    fake_path.exists.return_value = False
    mock_file.return_value = fake_path

    result = read_log_file("/fake/path.log", ssh=None)

    assert result == ["No logs found"]


def test_read_log_file_returns_lines(mocker: MockerFixture):
    mock_file_class = mocker.patch("cronboard.services.logging.logger.Path")

    fake_path = mocker.Mock()
    fake_path.exists.return_value = True
    mock_file_class.return_value = fake_path

    mock_open = mocker.mock_open(read_data="line1\nline2\nline3\n")
    mocker.patch("builtins.open", mock_open)

    result = read_log_file("/fake/path.log", ssh=None)

    assert result == ["line1\n", "line2\n", "line3\n"]