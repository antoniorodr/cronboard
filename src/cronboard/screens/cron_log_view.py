from paramiko.client import SSHClient
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button

from cronboard.widgets.cron_log_view import LogView


class LogViewModal(ModalScreen[bool]):
    """Modal screen for viewing a log file.

    Attributes:
        identificator: The identificator of the cronjob.
        ssh_client: Paramiko SSH client for remote operations.
    """

    def __init__(self, identificator: str, ssh_client=None):
        super().__init__()
        self.identificator: str = identificator
        self.ssh_client: SSHClient | None = ssh_client

    def compose(self) -> ComposeResult:
        """Builds the modal UI: log viewer."""

        yield Grid(
            LogView(identificator=self.identificator, ssh_client=self.ssh_client),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles button presses."""

        self.app.toggle_tab_enablement()
        self.dismiss(True)
