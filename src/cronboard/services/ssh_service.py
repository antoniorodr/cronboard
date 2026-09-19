from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cronboard.widgets.cron_table import CronTable


class SSHService:
    """Service class for SSH operations."""

    @staticmethod
    def execute_ssh_command(crontable: "CronTable", command: str):

        if crontable.ssh_client:
            _, stdout, _ = crontable.ssh_client.exec_command(command)
            exit_status: str = stdout.channel.recv_exit_status()

            return exit_status, stdout.read().decode() if stdout else ""
