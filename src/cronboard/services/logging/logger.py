import paramiko
import shlex
import shutil
from pathlib import Path

LOG_DIR = ".cronboard/logs"

def get_log_files(identificator: str, ssh: paramiko.SSHClient | None = None):
    if ssh is None:
        log_dir = Path.home() / LOG_DIR
        if not log_dir.exists():
            return []
        return {
            p.stem: str(p)
            for p in log_dir.glob(f"{identificator}_*.log")
        }
    else: # check remote later
        return []
        # stdin, stdout, stderr = ssh.exec_command("echo $HOME")
        # home = stdout.read().decode().strip()
        # log_dir = f"{home}/{LOG_DIR}"
        # stdin, stdout, stderr = ssh.exec_command(f"ls {log_dir} 2>/dev/null | grep ^{identificator}_.*\\.log$")
        # files = stdout.read().decode().strip().split("\n")
        # return [f"{log_dir}/{file}" for file in files if file]


def read_log_file(log_path: str, ssh: paramiko.SSHClient | None = None):
    if ssh is None:
        log_file = Path(log_path)
        if not log_file.exists():
            return ["No logs found"]
        with open(log_file, "r") as f:
            return f.readlines()
    else:
        return []
        # stdin, stdout, stderr = ssh.exec_command(f"cat {log_path}")
        # return stdout.read().decode().splitlines()