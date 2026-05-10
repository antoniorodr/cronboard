from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from cronboard.services.logging.logger import get_log_files, read_log_file

_LOGGER = "cronboard.services.logging.logger"
_FAKE_HOME = Path("/fake/home")


def _patch_local_log_discovery(
    mocker: MockerFixture,
    *,
    dir_exists: bool,
    glob_paths: list[Path] | None = None,
) -> None:
    mocker.patch(f"{_LOGGER}.Path.home", return_value=_FAKE_HOME)
    mocker.patch.object(Path, "exists", return_value=dir_exists)
    if glob_paths is not None:
        mocker.patch.object(Path, "glob", return_value=glob_paths)


def _ssh_mock_home_then_ls(
    mocker: MockerFixture,
    *,
    home_read: bytes,
    ls_read: bytes,
):
    ssh = mocker.Mock()
    stdout_home = mocker.Mock()
    stdout_home.read.return_value = home_read
    stdout_ls = mocker.Mock()
    stdout_ls.read.return_value = ls_read
    stderr = mocker.Mock()
    stderr.read.return_value = b""
    ssh.exec_command.side_effect = [
        (None, stdout_home, stderr),
        (None, stdout_ls, stderr),
    ]
    return ssh


def _patch_logger_path_and_instance(
    mocker: MockerFixture,
    *,
    exists: bool,
) -> None:
    mock_cls = mocker.patch(f"{_LOGGER}.Path")
    fake_path = mocker.Mock()
    fake_path.exists.return_value = exists
    mock_cls.return_value = fake_path


def _ssh_mock_single_exec(
    mocker: MockerFixture,
    *,
    stdout_read: bytes,
    stderr_read: bytes,
):
    ssh = mocker.Mock()
    stdout = mocker.Mock()
    stdout.read.return_value = stdout_read
    stderr = mocker.Mock()
    stderr.read.return_value = stderr_read
    ssh.exec_command.return_value = (None, stdout, stderr)
    return ssh


def test_get_log_files_returns_empty_when_dir_missing(mocker: MockerFixture):
    _patch_local_log_discovery(mocker, dir_exists=False)

    assert get_log_files("app1", ssh=None) == {}


def test_get_log_files_returns_dict(mocker: MockerFixture):
    fake_file1 = _FAKE_HOME / ".config/cronboard/logs/app1_log1.log"
    fake_file2 = _FAKE_HOME / ".config/cronboard/logs/app1_log2.log"

    _patch_local_log_discovery(
        mocker,
        dir_exists=True,
        glob_paths=[fake_file1, fake_file2],
    )

    assert get_log_files("app1", ssh=None) == {
        "app1_log1": str(fake_file1),
        "app1_log2": str(fake_file2),
    }


def test_get_log_files_returns_empty_dict_when_no_log_files_match_glob(
    mocker: MockerFixture,
):
    _patch_local_log_discovery(mocker, dir_exists=True, glob_paths=[])

    assert get_log_files("app1", ssh=None) == {}


def test_get_log_files_ssh_returns_empty_when_remote_home_unavailable(
    mocker: MockerFixture,
):
    mocker.patch(f"{_LOGGER}.get_remote_home", return_value=None)
    ssh = mocker.Mock()

    assert get_log_files("app1", ssh=ssh) == {}


@pytest.mark.parametrize(
    ("ls_read", "expected"),
    [
        (
            b"""app1_a.log
app1_b.log
app2_c.log
random.txt
""",
            {
                "app1_a": "/home/test/.config/cronboard/logs/app1_a.log",
                "app1_b": "/home/test/.config/cronboard/logs/app1_b.log",
            },
        ),
        (
            b"""other.log
file.txt
""",
            {},
        ),
    ],
    ids=["filtered", "no_match"],
)
def test_get_log_files_ssh(mocker: MockerFixture, ls_read: bytes, expected: dict):
    ssh = _ssh_mock_home_then_ls(
        mocker,
        home_read=b"/home/test\n",
        ls_read=ls_read,
    )

    assert get_log_files("app1", ssh=ssh) == expected


def test_read_log_file_returns_no_logs_when_missing(mocker: MockerFixture):
    _patch_logger_path_and_instance(mocker, exists=False)

    assert read_log_file("/fake/path.log", ssh=None) == []


def test_read_log_file_returns_lines(mocker: MockerFixture):
    _patch_logger_path_and_instance(mocker, exists=True)

    mock_open = mocker.mock_open(read_data="line1\nline2\nline3\n")
    mocker.patch("builtins.open", mock_open)

    assert read_log_file("/fake/path.log", ssh=None) == [
        "line1\n",
        "line2\n",
        "line3\n",
    ]


@pytest.mark.parametrize(
    ("stdout_read", "stderr_read", "remote_path", "expected"),
    [
        (
            b"line1\nline2\n",
            b"",
            "/remote/log.log",
            ["line1\n", "line2\n"],
        ),
        (
            b"",
            b"some error",
            "/remote/missing.log",
            [],
        ),
    ],
    ids=["success", "missing"],
)
def test_read_log_file_ssh(
    mocker: MockerFixture,
    stdout_read: bytes,
    stderr_read: bytes,
    remote_path: str,
    expected: list[str],
):
    ssh = _ssh_mock_single_exec(
        mocker,
        stdout_read=stdout_read,
        stderr_read=stderr_read,
    )

    assert read_log_file(remote_path, ssh=ssh) == expected


def test_read_log_file_ssh_empty_stdout_and_stderr(mocker: MockerFixture):
    ssh = _ssh_mock_single_exec(mocker, stdout_read=b"", stderr_read=b"")

    assert read_log_file("/remote/empty.log", ssh=ssh) == []


def test_read_log_file_ssh_returns_empty_when_stderr_has_noise(
    mocker: MockerFixture,
):
    ssh = _ssh_mock_single_exec(
        mocker,
        stdout_read=b"line\n",
        stderr_read=b"warning: cat wrote to stderr\n",
    )

    assert read_log_file("/remote/log.log", ssh=ssh) == []
