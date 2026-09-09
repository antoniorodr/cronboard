from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cronboard.widgets.cron_table import CronTable

from crontab import CronTab

from cronboard.screens.cron_ssh_modal import CronSSHModal
from cronboard.services.cron_logging.cron_wrapper import (
    command_without_wrapper,
    wrap_command,
)


class CronJobServices:
    @staticmethod
    def find_if_cronjob_exists(
        ssh_cron, remote, ssh_client, cron, server_name, identificator: str, cmd: str
    ):
        """Finds the CronJob in the local or remote CronTab.

        Args:
            identificator: The identificator of the cronjob.
            cmd: The command to execute.

        Returns:
            The CronJob if found, else None.
        """

        cron_to_use: CronTab | None = ssh_cron if (remote and ssh_client) else cron

        cmd_variants: set = {
            cmd,
            wrap_command(
                cmd,
                identificator,
                ssh_client if remote and ssh_client else None,
                server_name,
            ),
            command_without_wrapper(cmd),
        }

        for job in cron_to_use:
            if job.comment == identificator and job.command in cmd_variants:
                return job
        return None

    @staticmethod
    def write_remote_crontab(remote, ssh_client, ssh_cron, crontab_user):
        """Writes the current SSH cron table back to the remote server.

        Returns:
            True if success. Else False.
        """

        if not (remote and ssh_client and ssh_cron):
            return False

        try:
            new_crontab_content: CronSSHModal = ssh_cron.render()

            crontab_cmd: str = (
                f"crontab -u {crontab_user} -" if crontab_user else "crontab -"
            )
            stdin, _, stderr = ssh_client.exec_command(crontab_cmd)
            stdin.write(new_crontab_content)
            stdin.channel.shutdown_write()

            exit_status: str = stdin.channel.recv_exit_status()
            errors: str = stderr.read().decode().strip()

            if errors:
                print(f"❌ Failed to write remote crontab: {errors}")
                return False

            if exit_status != 0:
                print(f"❌ Command failed with exit status: {exit_status}")
                return False

            print("✅ Remote crontab updated successfully")
            return True

        except Exception as e:
            print(f"❌ Error writing remote crontab: {e}")
            return False

    @staticmethod
    def pause_cronjob(
        ssh_cron,
        remote,
        ssh_client,
        cron,
        server_name,
        crontab_user,
        identificator: str,
        cmd: str,
        crontable,
    ):
        """Pauses the selected cronjob."""

        cron_to_use: CronTab | None = ssh_cron if (remote and ssh_client) else cron

        job_to_toggle = CronJobServices.find_if_cronjob_exists(
            ssh_cron,
            remote,
            ssh_client,
            cron,
            server_name,
            identificator,
            cmd,
        )

        if job_to_toggle is None:
            job_to_toggle = CronJobServices.find_if_cronjob_exists(
                ssh_cron,
                remote,
                None,
                cron,
                server_name,
                identificator,
                wrap_command(
                    cmd,
                    identificator,
                    ssh_client if remote and ssh_client else None,
                    server_name,
                ),
            )

        if job_to_toggle is None:
            job_to_toggle = CronJobServices.find_if_cronjob_exists(
                ssh_cron,
                remote,
                None,
                cron,
                server_name,
                identificator,
                command_without_wrapper(cmd),
            )

        if job_to_toggle:
            job_to_toggle.enable(
                False
            ) if job_to_toggle.is_enabled() else job_to_toggle.enable(True)

            if remote and ssh_client:
                CronJobServices.write_remote_crontab(
                    remote, ssh_client, ssh_cron, crontab_user
                )
            else:
                cron_to_use.write()
            CronJobServices.load_crontabs(crontable)

    @staticmethod
    def load_crontabs(crontable: "CronTable") -> None:
        """Loads the crontabs."""

        crontable.clear()
        crontable._rows_data: list = []
        crontable._search_matches: list = []
        crontable._search_index = -1
        crontable._search_query = ""

        if crontable.remote and crontable.ssh_client:
            crontable.parse_cron(crontable.ssh_cron)

        else:
            crontable.parse_cron(crontable.cron)
