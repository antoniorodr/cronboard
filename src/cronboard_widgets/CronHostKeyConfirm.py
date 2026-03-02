from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class CronHostKeyConfirm(ModalScreen[bool]):
    """Modal shown when connecting to a host whose key is not yet trusted."""

    BINDINGS = [Binding(key="escape", action="cancel", description="Cancel")]

    def __init__(self, host: str, port: int, key_type: str, fingerprint: str) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._key_type = key_type
        self._fingerprint = fingerprint

    def compose(self) -> ComposeResult:
        yield Grid(
            Vertical(
                Label("Unknown host key", id="label1"),
                Label(
                    f"Host:        {self._host}:{self._port}",
                    id="label_host",
                ),
                Label(f"Key type:    {self._key_type}", id="label_type"),
                Label(f"Fingerprint: {self._fingerprint}", id="label_fp"),
                Label(
                    "Verify this fingerprint matches your server before trusting.\n"
                    "Connecting to the wrong host puts your crontab data at risk.",
                    id="label_hint",
                ),
                Horizontal(
                    Button("Trust and connect", variant="primary", id="trust"),
                    Button("Cancel", variant="error", id="cancel"),
                    id="button-row",
                ),
                id="content",
            ),
            id="dialog",
        )

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "trust")
