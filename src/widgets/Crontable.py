from crontab import CronTab
from textual.widgets import DataTable
import cronexpr
from textual.binding import Binding


class CronTable(DataTable):
    BINDINGS = [
        Binding("l", "cursor_right", "Right"),
        Binding("h", "cursor_left", "Left"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("c", "create_cronjob_keybind", "Create"),
        Binding("D", "delete_cronjob", "Delete"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "deactivate_cronjob", "Deactivate"),
        Binding("e", "edit_cronjob", "Edit"),
    ]

    def on_mount(self) -> None:
        self.cron: CronTab = CronTab(user=True)
        self.add_columns(
            "Identificator", "Expression", "Command", "Last Run", "Next Run", "Status"
        )
        self.load_crontabs()

    def load_crontabs(self):
        print("load_crontabs: refresh triggered")
        self.clear()

        for job in self.cron:
            expr = job.slices.render()
            cmd = job.command
            identificator = job.comment if job.comment else "No ID"
            try:
                next_dt = cronexpr.next_fire(expr).strftime("%d.%m.%Y at %H:%M")
                last_dt = cronexpr.prev_fire(expr).strftime("%d.%m.%Y at %H:%M")
                active_status = "Active" if job.is_enabled() else "Inactive"

                if active_status == "Inactive":
                    next_dt = "Stopped"

            except ValueError as e:
                next_dt = f"ERR: {e}"
                last_dt = f"ERR: {e}"
                active_status = "Inactive"
            self.add_row(
                identificator, expr, cmd, str(last_dt), str(next_dt), active_status
            )

        self.refresh()

    def action_create_cronjob_keybind(self) -> None:
        """Handle create cronjob action by calling the main app's method."""
        self.app.action_create_cronjob_keybind()

    def action_edit_cronjob_keybind(self, identificator, expression, command) -> None:
        self.app.action_edit_cronjob_keybind(
            identificator=identificator, expression=expression, command=command
        )

    def action_refresh(self) -> None:
        """Refresh the cronjob list."""
        self.cron = CronTab(user=True)
        self.load_crontabs()

    def action_deactivate_cronjob(self) -> None:
        if self.cursor_row is None:
            return

        row = self.get_row_at(self.cursor_row)
        identificator = row[0]
        expr = row[1]
        cmd = row[2]

        job_to_toggle = None
        for job in self.cron:
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
            self.cron.write()
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
            self.cron.remove(job_to_delete)
            self.cron.write()
            self.load_crontabs()

    def find_if_cronjob_exists(self, identificator: str, cmd: str):
        for job in self.cron:
            if job.comment == identificator and job.command == cmd:
                return job
        return None
