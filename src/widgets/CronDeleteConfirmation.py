from textual.app import ComposeResult
from crontab import CronTab
from textual.widgets import Button, Label
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen


class CronDeleteConfirmation(ModalScreen[bool]):
    def __init__(self, job) -> None:
        super().__init__()
        self.job = job
        self.cron = CronTab(user=True)

    def compose(self) -> ComposeResult:
        yield Grid(
            Vertical(
                Label(
                    f"Are you sure you want to delete '{self.job.comment}' ?",
                    id="label1",
                ),
                Horizontal(
                    Button("Delete", variant="primary", id="delete"),
                    Button("Cancel", variant="error", id="cancel"),
                    id="button-row",
                ),
                id="content",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "delete":
            self.dismiss(False)
            return

        self.cron.remove(self.job)
        self.cron.write()

        self.dismiss(True)
