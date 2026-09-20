from typing import TYPE_CHECKING

import paramiko

if TYPE_CHECKING:
    from cronboard.widgets.cron_table import CronTable


class SSHService:
    """Service class for SSH operations."""

    @staticmethod
    def execute_ssh_command(crontable: "CronTable", command: str):
        """Executes a command on a remote server.

        Args:
            crontable: The CronTable widget.
            command: The command to execute.

        Returns: A tuple with the exit status and the output of the command.

        """
        if crontable.ssh_client:
            _, stdout, _ = crontable.ssh_client.exec_command(command)
            exit_status: str = stdout.channel.recv_exit_status()

            return exit_status, stdout.read().decode() if stdout else ""

    @staticmethod
    def connect_to_ssh_server(
        server_info: dict,
    ) -> tuple[paramiko.SSHClient, str, int, str, str]:
        """Connects to a remote server.

        Args:
            server_info: The server information.

        Returns: A tuple with the SSHClient, host, port, username and password.

        """

        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)

        host = server_info["host"]
        port = server_info["port"]
        username = server_info["username"]
        password = server_info["password"]

        if server_info["ssh_key"]:
            ssh_client.connect(hostname=host, port=port, username=username)
        else:
            ssh_client.connect(
                hostname=host, port=port, username=username, password=password
            )

        return ssh_client, host, port, username, password

    @staticmethod
    def disconnect_from_ssh_server(ssh_client: paramiko.SSHClient) -> None:
        """Disconnects from a remote server.
        Args:
            ssh_client: The SSHClient.
        """
        ssh_client.close()
