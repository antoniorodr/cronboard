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


def test_get_log_files_ssh_returns_filtered_logs(mocker: MockerFixture):
    ssh = mocker.Mock()

    # Mock "echo $HOME"
    stdout_home = mocker.Mock()
    stdout_home.read.return_value = b"/home/test\n"

    # Mock "ls"
    stdout_ls = mocker.Mock()
    stdout_ls.read.return_value = b"""app1_a.log
app1_b.log
app2_c.log
random.txt
"""

    stderr = mocker.Mock()
    stderr.read.return_value = b""

    ssh.exec_command.side_effect = [
        (None, stdout_home, stderr),  # echo $HOME
        (None, stdout_ls, stderr),    # ls
    ]

    from cronboard.services.logging.logger import get_log_files

    result = get_log_files("app1", ssh=ssh)

    assert result == {
        "app1_a": "/home/test/.cronboard/logs/app1_a.log",
        "app1_b": "/home/test/.cronboard/logs/app1_b.log",
    }


def test_get_log_files_ssh_no_matching_logs(mocker: MockerFixture):
    ssh = mocker.Mock()

    stdout_home = mocker.Mock()
    stdout_home.read.return_value = b"/home/test\n"

    stdout_ls = mocker.Mock()
    stdout_ls.read.return_value = b"""other.log
file.txt
"""

    stderr = mocker.Mock()
    stderr.read.return_value = b""

    ssh.exec_command.side_effect = [
        (None, stdout_home, stderr),
        (None, stdout_ls, stderr),
    ]

    from cronboard.services.logging.logger import get_log_files

    result = get_log_files("app1", ssh=ssh)

    assert result == {}


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


def test_read_log_file_ssh_success(mocker: MockerFixture):
    ssh = mocker.Mock()

    stdout = mocker.Mock()
    stdout.read.return_value = b"line1\nline2\n"

    stderr = mocker.Mock()
    stderr.read.return_value = b""

    ssh.exec_command.return_value = (None, stdout, stderr)

    from cronboard.services.logging.logger import read_log_file

    result = read_log_file("/remote/log.log", ssh=ssh)

    assert result == ["line1\n", "line2\n"]


def test_read_log_file_ssh_file_missing(mocker: MockerFixture):
    ssh = mocker.Mock()

    stdout = mocker.Mock()
    stdout.read.return_value = b""

    stderr = mocker.Mock()
    stderr.read.return_value = b"some error"

    ssh.exec_command.return_value = (None, stdout, stderr)

    from cronboard.services.logging.logger import read_log_file

    result = read_log_file("/remote/missing.log", ssh=ssh)

    assert result == ["No logs found"]