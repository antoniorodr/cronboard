from crontab import CronTab
from textual.widgets import DataTable
import cronexpr
from textual.binding import Binding


class CronTable(DataTable):
    BINDINGS = [
        Binding("l", "cursor_right", "Right"),
        Binding("h", "cursor_left", "Left"),
        Binding("c", "create_cronjob_keybind", "Create cronjob"),
    ]

    def on_mount(self) -> None:
        self.cron: CronTab = CronTab(user=True)
        self.load_crontabs()

    def load_crontabs(self):
        self.clear()
        self.add_columns("Expression", "Action", "Last Run", "Next Run", "Active")

        for job in self.cron:
            expr = job.slices.render()
            cmd = job.command
            try:
                next_dt = cronexpr.next_fire(expr).strftime("%d.%m.%Y at %H:%M")
                last_dt = cronexpr.prev_fire(expr).strftime("%d.%m.%Y at %H:%M")
                active_status = "✓" if job.is_enabled() else "✗"
            except ValueError as e:
                next_dt = f"ERR: {e}"
                last_dt = f"ERR: {e}"
                active_status = "✗"
            self.add_row(expr, cmd, str(last_dt), str(next_dt), active_status)
