import shlex
from shutil import which

import crontab as crontab_module
from crontab import CronTab


def get_local_crontab_command() -> str:
    """Return the installed crontab-compatible command."""
    for command in ("crontab", "fcrontab"):
        command_path = which(command)
        if command_path:
            return command_path
    return crontab_module.CRON_COMMAND


def create_user_crontab() -> CronTab:
    """Create a user CronTab using crontab or fcrontab when available."""
    original_command = crontab_module.CRON_COMMAND
    crontab_module.CRON_COMMAND = get_local_crontab_command()
    try:
        return CronTab(user=True)
    finally:
        crontab_module.CRON_COMMAND = original_command


def remote_crontab_command(*args: str) -> str:
    quoted_args = " ".join(shlex.quote(str(arg)) for arg in args if arg)
    suffix = f" {quoted_args}" if quoted_args else ""
    return (
        "if command -v crontab >/dev/null 2>&1; "
        f"then crontab{suffix}; "
        f"else fcrontab{suffix}; fi"
    )


def remote_crontab_list_command(crontab_user: str | None = None) -> str:
    if crontab_user:
        return remote_crontab_command("-u", crontab_user, "-l")
    return remote_crontab_command("-l")


def remote_crontab_write_command(crontab_user: str | None = None) -> str:
    if crontab_user:
        return remote_crontab_command("-u", crontab_user, "-")
    return remote_crontab_command("-")
