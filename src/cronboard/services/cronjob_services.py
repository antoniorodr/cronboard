from crontab import CronTab

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
