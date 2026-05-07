import os
import stat
from pathlib import Path
import pytest
from pytest_mock import MockerFixture
import cronboard.services.logging.cron_wrapper as mod

def test_is_wrapper_installed_local_true(
    mocker: MockerFixture, tmp_path
):
    home = tmp_path / "home"
    home.mkdir(parents=True)

    mocker.patch("cronboard.services.logging.cron_wrapper.Path.home", return_value=home)

    wrapper_source = tmp_path / "cron-wrapper.sh"
    wrapper_source.write_text("#!/bin/sh\necho test")

    mocker.patch.object(mod, "WRAPPER_SOURCE", wrapper_source)

    result = mod.install_wrapper_local()

    assert mod.is_wrapper_installed_local() is True


def test_is_wrapper_installed_local_false(
    mocker: MockerFixture, tmp_path
):
    home = tmp_path / "home"
    mocker.patch.object(mod.Path, "home", return_value=home)

    assert mod.is_wrapper_installed_local() is False


def test_is_wrapper_installed_remote_true(
    mocker: MockerFixture
):
    ssh = mocker.Mock()

    def exec_command(cmd):
        mock_stdout = mocker.Mock()

        if cmd == "echo $HOME":
            mock_stdout.read.return_value = b"/home/user\n"
        else:
            mock_stdout.read.return_value = b"OK\n"

        return (None, mock_stdout, None)

    ssh.exec_command.side_effect = exec_command

    assert mod.is_wrapper_installed_remote(ssh) is True


def test_is_wrapper_installed_remote_false(
    mocker: MockerFixture
):
    ssh = mocker.Mock()

    def exec_command(cmd):
        mock_stdout = mocker.Mock()

        if cmd == "echo $HOME":
            mock_stdout.read.return_value = b"/home/user\n"
        else:
            mock_stdout.read.return_value = b"MISSING\n"

        return (None, mock_stdout, None)

    ssh.exec_command.side_effect = exec_command

    assert mod.is_wrapper_installed_remote(ssh) is False

def test_install_wrapper_local_creates_dir_and_copies_and_sets_executable(
    mocker: MockerFixture, tmp_path
):
    home = tmp_path / "home"
    home.mkdir(parents=True)

    mocker.patch.object(mod.Path, "home", return_value=home)

    wrapper_source = tmp_path / "cron-wrapper.sh"
    wrapper_source.write_bytes(b"#!/bin/sh\necho hello\n")

    mocker.patch.object(mod, "WRAPPER_SOURCE", wrapper_source)

    out_path_str = mod.install_wrapper_local()
    out_path = Path(out_path_str)

    assert out_path == home / ".cronboard" / "cron-wrapper.sh"
    assert out_path.exists()
    assert out_path.read_bytes() == wrapper_source.read_bytes()

    mode = out_path.stat().st_mode
    assert mode & stat.S_IEXEC

    assert out_path.parent.name == ".cronboard"


def test_install_wrapper_remote_executes_expected_commands_and_returns_remote_path(
    mocker: MockerFixture
):
    ssh = mocker.Mock(spec=["exec_command", "open_sftp"])

    stdout = mocker.Mock()
    stdout.read.return_value = b"/remote/home/user\n"

    ssh.exec_command.return_value = (mocker.Mock(), stdout, mocker.Mock())

    sftp = mocker.Mock()
    ssh.open_sftp.return_value = sftp

    local_wrapper_source = "/some/local/cron-wrapper.sh"
    mocker.patch.object(mod, "WRAPPER_SOURCE", Path(local_wrapper_source))

    remote_path = mod.install_wrapper_remote(ssh)

    expected_remote_dir = "/remote/home/user/.cronboard"
    expected_remote_file = f"{expected_remote_dir}/cron-wrapper.sh"

    assert remote_path == expected_remote_file

    ssh.exec_command.assert_any_call("echo $HOME")

    ssh.exec_command.assert_any_call(f"mkdir -p {expected_remote_dir}")
    ssh.exec_command.assert_any_call(f"chmod +x {expected_remote_file}")

    sftp.put.assert_called_once_with(
        str(mod.WRAPPER_SOURCE),
        expected_remote_file,
    )

    sftp.close.assert_called_once_with()


def test_install_wrapper_remote_closes_sftp_even_if_put_raises(
    mocker: MockerFixture
):
    ssh = mocker.Mock(spec=["exec_command", "open_sftp"])

    stdout = mocker.Mock()
    stdout.read.return_value = b"/remote/home/user\n"
    ssh.exec_command.return_value = (mocker.Mock(), stdout, mocker.Mock())

    sftp = mocker.Mock()
    sftp.put.side_effect = RuntimeError("upload failed")
    ssh.open_sftp.return_value = sftp

    mocker.patch.object(mod, "WRAPPER_SOURCE", Path("/local/cron-wrapper.sh"))

    with pytest.raises(RuntimeError, match="upload failed"):
        mod.install_wrapper_remote(ssh)

    sftp.close.assert_called_once_with()


def test_install_wrapper_calls_local_when_ssh_is_none(
    mocker: MockerFixture
):
    mock_local = mocker.patch.object(mod, "install_wrapper_local", return_value="/local/path")
    res = mod.install_wrapper(ssh=None)
    assert res == "/local/path"
    mock_local.assert_called_once_with()


def test_install_wrapper_calls_remote_when_ssh_provided(
    mocker: MockerFixture
):
    ssh = mocker.Mock()
    mock_remote = mocker.patch.object(mod, "install_wrapper_remote", return_value="/remote/path")
    res = mod.install_wrapper(ssh=ssh)
    assert res == "/remote/path"
    mock_remote.assert_called_once_with(ssh)

def test_wrap_command_basic(mocker: MockerFixture):
    mocker.patch.object(mod, "install_wrapper", return_value="/tmp/cron-wrapper.sh")
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    res = mod.wrap_command("echo hello", "job-1")

    assert res == "/bin/bash /tmp/cron-wrapper.sh job-1 echo hello"


def test_wrap_command_fallback_bash(mocker: MockerFixture):
    mocker.patch.object(mod, "install_wrapper", return_value="/tmp/cron-wrapper.sh")
    mocker.patch.object(mod.shutil, "which", return_value=None)

    res = mod.wrap_command("echo hello", "job-1")

    assert res == "/bin/bash /tmp/cron-wrapper.sh job-1 echo hello"


def test_wrap_command_with_already_wrapped_command(mocker: MockerFixture):
    mocker.patch.object(mod, "install_wrapper", return_value="/tmp/cron-wrapper.sh")
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/cron-wrapper.sh job-1 echo hello"
    res = mod.wrap_command(cmd, "job-1")

    assert res == cmd


def test_wrap_command_includes_identificator(mocker: MockerFixture):
    mocker.patch.object(mod, "install_wrapper", return_value="/tmp/cron-wrapper.sh")
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    res = mod.wrap_command("echo hello", "job-42")

    assert res == "/bin/bash /tmp/cron-wrapper.sh job-42 echo hello"


def test_has_wrapper_valid(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/cron-wrapper.sh job-1 echo hello"
    assert mod.has_wrapper(cmd) is True


def test_has_wrapper_missing_identificator(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/cron-wrapper.sh echo hello" # echo is identificator here
    assert mod.has_wrapper(cmd) is True


def test_has_wrapper_wrong_bash(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/usr/bin/bash /tmp/cron-wrapper.sh job-1 echo hello"
    assert mod.has_wrapper(cmd) is False


def test_has_wrapper_non_wrapper1(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/not-wrapper.sh job-1 echo hello"
    assert mod.has_wrapper(cmd) is False

def test_has_wrapper_non_wrapper2(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "echo hello"
    assert mod.has_wrapper(cmd) is False


def test_command_without_wrapper_valid(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/cron-wrapper.sh job-1 echo hello world"
    res = mod.command_without_wrapper(cmd)

    assert res == "echo hello world"


def test_command_without_wrapper_wrong_bash(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/usr/bin/bash /tmp/cron-wrapper.sh job-1 echo hello"
    res = mod.command_without_wrapper(cmd)

    assert res == cmd


def test_command_without_wrapper_non_wrapper(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/not-wrapper.sh job-1 echo hello"
    res = mod.command_without_wrapper(cmd)

    assert res == cmd


def test_command_without_wrapper_too_short(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/cron-wrapper.sh job-1"
    res = mod.command_without_wrapper(cmd)

    assert res == cmd


def test_command_without_wrapper_parse_error(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/cron-wrapper.sh job-1 'unterminated"
    res = mod.command_without_wrapper(cmd)

    assert res == cmd


def test_command_without_wrapper_complex_command(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = '/bin/bash /tmp/cron-wrapper.sh job-1 python3 script.py --arg "value with spaces"'
    res = mod.command_without_wrapper(cmd)

    assert res == "python3 script.py --arg value with spaces"


def test_command_without_wrapper_passthrough(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "python3 script.py --arg s"
    res = mod.command_without_wrapper(cmd)

    assert res == cmd


def test_command_without_wrapper_missing_command(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "/bin/bash /tmp/cron-wrapper.sh job-1"
    res = mod.command_without_wrapper(cmd)

    assert res == cmd


def test_command_without_wrapper_extra_spaces(mocker: MockerFixture):
    mocker.patch.object(mod.shutil, "which", return_value="/bin/bash")

    cmd = "  /bin/bash   /tmp/cron-wrapper.sh   job-1   echo   hello  "
    res = mod.command_without_wrapper(cmd)

    assert res == "echo hello"