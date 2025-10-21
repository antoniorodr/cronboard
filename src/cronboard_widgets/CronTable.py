from crontab import CronTab
from textual.widgets import DataTable
from textual.binding import Binding
from datetime import datetime


class CronTable(DataTable):
    BINDINGS = [
        Binding("l", "cursor_right", "Right"),
        Binding("h", "cursor_left", "Left"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("c", "create_cronjob_keybind", "Create"),
        Binding("D", "delete_cronjob", "Delete"),
        Binding("r", "refresh", "Refresh"),
        Binding("p", "pause_cronjob", "Pause Toggle"),
        Binding("e", "edit_cronjob", "Edit"),
    ]

    def __init__(self, remote=False, ssh_client=None, **kwargs):
        super().__init__(**kwargs)
        self.remote = remote
        self.ssh_client = ssh_client

    def on_mount(self) -> None:
        self.cron: CronTab = CronTab(user=True)
        self.add_columns(
            "Identificator", "Expression", "Command", "Last Run", "Next Run", "Status"
        )

        if self.remote and self.ssh_client:
            _, stdout, _ = self.ssh_client.exec_command("crontab -l")
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 1:
                self.crontab_content = ""
            else:
                self.crontab_content = stdout.read().decode() if stdout else ""

            self.ssh_cron: CronTab | None = CronTab(tab=self.crontab_content)
        else:
            self.ssh_cron = None

        self.load_crontabs()

    def parse_cron(self, cron):
        for job in cron:
            expr = job.slices.render()
            cmd = job.command
            identificator = job.comment if job.comment else "No ID"
            try:
                active_status = "Active" if job.is_enabled() else "Paused"
                schedule = job.schedule(date_from=datetime.now())
                next_dt = (
                    schedule.get_next().strftime("%d.%m.%Y at %H:%M")
                    if active_status == "Active"
                    else "Paused"
                )
                last_dt = schedule.get_prev().strftime("%d.%m.%Y at %H:%M")

                if active_status == "Inactive":
                    next_dt = "Stopped"

            except ValueError as e:
                next_dt = f"ERR: {e}"
                last_dt = f"ERR: {e}"
                active_status = "Inactive"
            self.add_row(
                identificator, expr, cmd, str(last_dt), str(next_dt), active_status
            )

    def load_crontabs(self):
        self.clear()

        if self.remote and self.ssh_client:
            self.parse_cron(self.ssh_cron)

        else:
            self.parse_cron(self.cron)

    def action_create_cronjob_keybind(self) -> None:
        """Handle create cronjob action by calling the main app's method."""
        used_cron = self.ssh_cron if self.remote and self.ssh_client else self.cron
        self.app.action_create_cronjob(
            used_cron, remote=self.remote, ssh_client=self.ssh_client
        )

    def action_edit_cronjob_keybind(self, identificator, expression, command) -> None:
        used_cron = self.ssh_cron if self.remote and self.ssh_client else self.cron
        self.app.action_edit_cronjob(
            used_cron,
            identificator=identificator,
            expression=expression,
            command=command,
            remote=self.remote,
            ssh_client=self.ssh_client,
        )

    def action_delete_cronjob_keybind(self, job) -> None:
        used_cron = self.ssh_cron if self.remote and self.ssh_client else self.cron
        self.app.action_delete_cronjob(
            job, cron=used_cron, remote=self.remote, ssh_client=self.ssh_client
        )

    def action_refresh(self) -> None:
        """Refresh the cronjob list."""
        if self.remote and self.ssh_client:
            _, stdout, _ = self.ssh_client.exec_command("crontab -l")
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 1:
                self.crontab_content = ""
            else:
                self.crontab_content = stdout.read().decode() if stdout else ""

            self.ssh_cron = CronTab(tab=self.crontab_content)
        else:
            self.cron = CronTab(user=True)
        self.load_crontabs()

    def action_pause_cronjob(self) -> None:
        if self.cursor_row is None:
            return

        row = self.get_row_at(self.cursor_row)
        identificator = row[0]
        expr = row[1]
        cmd = row[2]

        cron_to_use = self.ssh_cron if (self.remote and self.ssh_client) else self.cron

        job_to_toggle = None
        for job in cron_to_use:
            if (
                job.comment == identificator
                and job.slices.render() == expr
                and job.command == cmd
            ):
                job_to_toggle = job
                break

        if job_to_toggle:
            job_to_toggle.enable(
                False
            ) if job_to_toggle.is_enabled() else job_to_toggle.enable(True)

            if self.remote and self.ssh_client:
                self.write_remote_crontab()
            else:
                cron_to_use.write()
            self.load_crontabs()

    def action_edit_cronjob(self) -> None:
        if self.cursor_row is None:
            return

        row = self.get_row_at(self.cursor_row)
        identificator = row[0]
        expr = row[1]
        cmd = row[2]

        job_to_edit = self.find_if_cronjob_exists(identificator, cmd)

        if job_to_edit:
            self.action_edit_cronjob_keybind(identificator, expr, cmd)

    def action_delete_cronjob(self) -> None:
        """Delete the selected cronjob."""
        if self.cursor_row is None:
            return

        row = self.get_row_at(self.cursor_row)
        identificator = row[0]
        cmd = row[2]

        job_to_delete = self.find_if_cronjob_exists(identificator, cmd)

        if job_to_delete:
            self.action_delete_cronjob_keybind(job_to_delete)

    def find_if_cronjob_exists(self, identificator: str, cmd: str):
        cron_to_use = self.ssh_cron if (self.remote and self.ssh_client) else self.cron

        for job in cron_to_use:
            if job.comment == identificator and job.command == cmd:
                return job
        return None

    def action_disconnect_ssh(self) -> None:
        """Disconnect SSH connection and return to local cron tab."""
        if self.remote and self.ssh_client:
            self.app.action_disconnect_ssh()

    def write_remote_crontab(self):
        """Writes the current SSH cron table back to the remote server."""
        if not (self.remote and self.ssh_client and self.ssh_cron):
            return False

        try:
            new_crontab_content = self.ssh_cron.render()

            stdin, _, stderr = self.ssh_client.exec_command("crontab -")
            stdin.write(new_crontab_content)
            stdin.channel.shutdown_write()

            exit_status = stdin.channel.recv_exit_status()
            errors = stderr.read().decode().strip()

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
