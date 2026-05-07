import paramiko
import shlex
import shutil
from pathlib import Path
import posixpath

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
    else:
        stdin, stdout, stderr = ssh.exec_command("echo $HOME")
        home = stdout.read().decode().strip()
        log_dir = posixpath.join(home, LOG_DIR)

        cmd = f'ls {log_dir} 2>/dev/null'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        files = stdout.read().decode().splitlines()

        result = {}
        for file in files:
            if file.startswith(f"{identificator}_") and file.endswith(".log"):
                stem = file[:-4]  # remove ".log"
                full_path = posixpath.join(log_dir, file)
                result[stem] = full_path

        return result


def read_log_file(log_path: str, ssh: paramiko.SSHClient | None = None):
    if ssh is None:
        log_file = Path(log_path)
        if not log_file.exists():
            return ["No logs found"]
        with open(log_file, "r") as f:
            return f.readlines()
    else:
        safe_path = shlex.quote(log_path)

        stdin, stdout, stderr = ssh.exec_command(f"test -f {safe_path} && cat {safe_path}")
        output = stdout.read().decode()
        error = stderr.read().decode()

        if not output and error:
            return ["No logs found"]

        return output.splitlines(keepends=True)