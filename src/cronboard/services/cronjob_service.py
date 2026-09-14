from datetime import datetime
from typing import TYPE_CHECKING

from rich.text import Text
from textual.widgets import Input

if TYPE_CHECKING:
    from cronboard.screens.cron_creator import CronCreator
    from cronboard.widgets.cron_table import CronTable

from crontab import CronTab
from paramiko.client import SSHClient

from cronboard.screens.cron_ssh_modal import CronSSHModal
from cronboard.services.cron_logging.cron_wrapper import (
    command_without_wrapper,
    wrap_command,
)


class CronJobService:
    """Services for CronJob related operations."""

    @staticmethod
    def find_if_cronjob_exists(
        ssh_cron: CronTab | None,
        remote: bool,
        ssh_client: SSHClient | None,
        cron: CronTab,
        server_name: str,
        identificator: str,
        cmd: str,
    ) -> CronTab | None:
        """Finds the CronJob in the local or remote CronTab.

        Args:
            ssh_cron: CronTab instance for the remote CronTab.
            remote: Whether the user is on the remote CronTab.
            ssh_client: SSH client.
            cron: CronTab instance for the local CronTab.
            server_name: Server name if remote.
            identificator: Identificator of the cronjob.
            cmd:  Command to execute for the cronjob.

        Returns:
            CronJob if found, else None.

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
    def write_remote_crontab(remote, ssh_client, ssh_cron, crontab_user) -> bool:
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
    ) -> None:
        """Pauses the selected cronjob.

        Args:
            ssh_cron: CronTab instance for the remote CronTab.
            remote: Whether the user is on the remote CronTab.
            ssh_client: SSH client.
            cron: CronTab instance for the local CronTab.
            server_name: Server name if remote.
            crontab_user: CronTab user for the remote CronTab.
            identificator: Identificator of the cronjob.
            cmd:  Command to execute for the cronjob.
            crontable: The CronTable instance to populate.
        """
        cron_to_use: CronTab | None = ssh_cron if (remote and ssh_client) else cron

        job_to_toggle: CronTab | None = CronJobService.find_if_cronjob_exists(
            ssh_cron,
            remote,
            ssh_client,
            cron,
            server_name,
            identificator,
            cmd,
        )

        if job_to_toggle:
            job_to_toggle.enable(
                False
            ) if job_to_toggle.is_enabled() else job_to_toggle.enable(True)

            if remote and ssh_client:
                CronJobService.write_remote_crontab(
                    remote, ssh_client, ssh_cron, crontab_user
                )
            else:
                cron_to_use.write()
            CronJobService.load_crontabs(crontable)

    @staticmethod
    def load_crontabs(crontable: "CronTable") -> None:
        """Loads the crontabs.

        Args:
            crontable: The CronTable instance to populate.
        """
        crontable.clear()
        crontable._rows_data: list = []
        crontable._search_matches: list = []
        crontable._search_index = -1
        crontable._search_query = ""

        if crontable.remote and crontable.ssh_client:
            CronJobService.parse_cron(crontable, crontable.ssh_cron)

        else:
            CronJobService.parse_cron(crontable, crontable.cron)

    @staticmethod
    def parse_cron(crontable: "CronTable", cron) -> None:
        """Parses the crontab and populates the table.

        Args:
            cron: The CronTab instance to parse.
            crontable: The CronTable instance to populate.
        """

        for job in cron:
            expr: str = job.slices.render()
            cmd: str = command_without_wrapper(job.command)
            log_enabled: bool | None = crontable.has_log_enabled(
                job.comment, job.command
            )
            notifications_enabled: bool | None = crontable.has_notifications_enabled(
                job.comment
            )
            identificator: str = job.comment if job.comment else "No ID"
            try:
                active_status: str = "Active" if job.is_enabled() else "Paused"
                schedule = job.schedule(date_from=datetime.now())
                next_dt = (
                    schedule.get_next().strftime("%d.%m.%Y at %H:%M")
                    if active_status == "Active"
                    else "Paused"
                )
                last_dt = schedule.get_prev().strftime("%d.%m.%Y at %H:%M")

            except ValueError as e:
                next_dt = f"ERR: {e}"
                last_dt = f"ERR: {e}"
                active_status = "Inactive"

            if active_status == "Active":
                status_text = Text(active_status, style="#B8E7B8")
            elif active_status == "Paused":
                status_text = Text(active_status, style="#FF6F61")
            else:
                status_text = Text(active_status, style="#F6BF00")

            crontable.add_row(
                identificator,
                expr,
                cmd,
                str(log_enabled),
                str(notifications_enabled),
                str(last_dt),
                str(next_dt),
                status_text,
            )
            crontable._rows_data.append(
                (
                    identificator,
                    expr,
                    cmd,
                    str(log_enabled),
                    str(notifications_enabled),
                    str(last_dt),
                    str(next_dt),
                    status_text,
                )
            )

    @staticmethod
    def save_cronjob(cron_creator: "CronCreator") -> None:
        """Saves the cronjob on save. Shows errors if any.

        If the cronjob exists, it updates it. Else, it creates a new one.

        Args:
            cron_creator: The CronCreator instance.
        """

        # TODO: Move UI queries to CronCreator

        identificator_input: Input = cron_creator.query_one("#identificator", Input)
        expression_input: Input = cron_creator.query_one("#expression", Input)
        command_input: Input = cron_creator.query_one("#command", Input)
        expression: str = expression_input.value
        command: str = command_input.value
        identificator: str = identificator_input.value

        if not identificator:
            cron_creator._show_error("ID cannot be empty.")
            return

        if " " in identificator:
            cron_creator._show_error("ID cannot contain spaces. e.g., backup_job_1")
            return

        cron_creator.save_job_settings(
            identificator, cron_creator.notifications_enabled, cron_creator.log_enabled
        )
        if cron_creator.remote and cron_creator.ssh_client:
            cron_creator.push_notifications_to_remote()

        try:
            job = cron_creator.find_cronjob_in_cron_list(
                identificator, command_without_wrapper(command)
            )
            if not job:
                job = cron_creator.find_cronjob_in_cron_list(
                    identificator,
                    wrap_command(
                        command,
                        identificator,
                        cron_creator.ssh_client
                        if cron_creator.remote and cron_creator.ssh_client
                        else None,
                        cron_creator.server_name,
                    ),
                )
            if cron_creator.log_enabled or cron_creator.notifications_enabled:
                command = wrap_command(
                    command,
                    identificator,
                    cron_creator.ssh_client
                    if cron_creator.remote and cron_creator.ssh_client
                    else None,
                    cron_creator.server_name,
                )
            if job:
                job.set_command(command)
                job.setall(expression)
                CronJobService.write_cron_changes(cron_creator)
            else:
                cron_job = cron_creator.cron.new(command=command, comment=identificator)
                cron_job.setall(expression)
                CronJobService.write_cron_changes(cron_creator)

            cron_creator.dismiss(True)

        except (ValueError, KeyError):
            cron_creator._show_error("Invalid cron expression. Please try again.")

    @staticmethod
    def write_cron_changes(cron_creator: "CronCreator") -> None:
        """Write cron changes to appropriate destination (local or remote)

        Args:
            cron_creator: The CronCreator instance.
        """

        if cron_creator.remote and cron_creator.ssh_client:
            try:
                new_crontab_content = cron_creator.cron.render()
                crontab_cmd: str = (
                    f"crontab -u {cron_creator.crontab_user} -"
                    if cron_creator.crontab_user
                    else "crontab -"
                )
                stdin, _, stderr = cron_creator.ssh_client.exec_command(crontab_cmd)
                stdin.write(new_crontab_content)
                stdin.channel.shutdown_write()

                exit_status: str = stdin.channel.recv_exit_status()
                errors: str = stderr.read().decode().strip()

                if errors or exit_status != 0:
                    cron_creator.notify(f"Failed to write remote crontab: {errors}")

            except Exception as e:
                print(f"❌ Error writing remote crontab: {e}")
                raise
        else:
            cron_creator.cron.write()
