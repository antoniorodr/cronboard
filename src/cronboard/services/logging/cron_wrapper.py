import os
import stat
import paramiko
from pathlib import Path
import shlex
import shutil

WRAPPER_SOURCE = Path(__file__).parent.parent.parent / "logging" / "cron-wrapper.sh"
WRAPPER_DIST_DIR = ".cronboard"
WRAPPER_DIST = f"{WRAPPER_DIST_DIR}/cron-wrapper.sh"

def is_wrapper_installed_local() -> bool:
    target_file = Path.home() / WRAPPER_DIST

    return (
        target_file.exists()
        and target_file.is_file()
        and os.access(target_file, os.X_OK)
    )


def is_wrapper_installed_remote(ssh: paramiko.SSHClient) -> bool:
    stdin, stdout, stderr = ssh.exec_command("echo $HOME")
    home = stdout.read().decode().strip()

    remote_file = f"{home}/{WRAPPER_DIST}"

    stdin, stdout, stderr = ssh.exec_command(
        f"test -f {remote_file} && test -x {remote_file} && echo OK || echo MISSING"
    )

    result = stdout.read().decode().strip()
    return result == "OK"

def is_wrapper_installed(ssh: paramiko.SSHClient | None = None) -> bool:
    if ssh is None:
        return is_wrapper_installed_local()
    else:
        return is_wrapper_installed_remote(ssh)

def install_wrapper_local():
    target_dir = Path.home() / WRAPPER_DIST_DIR
    target_file = Path.home() / WRAPPER_DIST

    if is_wrapper_installed_local():
        return str(target_file)

    target_dir.mkdir(parents=True, exist_ok=True)

    with open(WRAPPER_SOURCE, "rb") as src, open(target_file, "wb") as dst:
        dst.write(src.read())
    
    target_file.chmod(target_file.stat().st_mode | stat.S_IEXEC)

    return str(target_file)


def install_wrapper_remote(ssh: paramiko.SSHClient):
    stdin, stdout, stderr = ssh.exec_command("echo $HOME")
    home = stdout.read().decode().strip()

    remote_dir = f"{home}/{WRAPPER_DIST_DIR}"
    remote_file = f"{home}/{WRAPPER_DIST}"

    if is_wrapper_installed_remote(ssh):
        return remote_file

    sftp = ssh.open_sftp()

    try:
        ssh.exec_command(f"mkdir -p {remote_dir}")
        sftp.put(str(WRAPPER_SOURCE), remote_file)
        ssh.exec_command(f"chmod +x {remote_file}")
    finally:
        sftp.close()

    return remote_file


def install_wrapper(ssh: paramiko.SSHClient | None = None):
    if ssh is None:
        return install_wrapper_local()
    else:
        return install_wrapper_remote(ssh)
    
def wrap_command(command: str, identificator: str, ssh: paramiko.SSHClient | None = None):
    wrapper_path = install_wrapper(ssh)
    bash_path = shutil.which("bash") or "/bin/bash"
    try:
        parts = shlex.split(command)
    except ValueError:
        # If it can't be parsed, just wrap it (safer than guessing)
        parts = []

    # Detect already wrapped command
    if (
        len(parts) >= 3
        and parts[0] == bash_path
        and parts[1].endswith("cron-wrapper.sh")
    ):
        return command
    return f"{shlex.quote(bash_path)} {wrapper_path} {identificator} {command}"

def has_wrapper(command: str) -> bool:
    bash_path = shutil.which("bash") or "/bin/bash"

    try:
        parts = shlex.split(command)
    except ValueError:
        return False

    if len(parts) < 4:
        return False

    if parts[0] != bash_path:
        return False

    wrapper_path = parts[1]

    return (
        wrapper_path.endswith("cron-wrapper.sh")
        and bool(parts[2])  # identificator
    )

def command_without_wrapper(command: str):
    bash_path = shutil.which("bash") or "/bin/bash"

    try:
        parts = shlex.split(command)
    except ValueError:
        return command

    if len(parts) < 4:
        return command

    if parts[0] != bash_path:
        return command

    wrapper_path = parts[1]

    if not wrapper_path.endswith("cron-wrapper.sh"):
        return command

    # strip: bash + wrapper + identificator
    return " ".join(parts[3:])