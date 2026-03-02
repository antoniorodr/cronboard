from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class CronHostKeyChanged(ModalScreen[bool]):
    """Modal shown when a host's key differs from the previously trusted one."""

    BINDINGS = [Binding(key="escape", action="cancel", description="Cancel")]

    def __init__(
        self,
        host: str,
        port: int,
        expected_fp: str,
        received_fp: str,
    ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._expected_fp = expected_fp
        self._received_fp = received_fp

    def compose(self) -> ComposeResult:
        yield Grid(
            Vertical(
                Label("Host key has CHANGED", id="label1", classes="error"),
                Label(
                    f"Host:     {self._host}:{self._port}",
                    id="label_host",
                ),
                Label(
                    f"Expected: {self._expected_fp}",
                    id="label_expected",
                ),
                Label(
                    f"Received: {self._received_fp}",
                    id="label_received",
                    classes="error",
                ),
                Label(
                    "This may indicate a MITM attack or a recent server re-install.\n"
                    "Verify the new fingerprint with your admin before trusting.",
                    id="label_hint",
                ),
                Horizontal(
                    Button("Trust new key", variant="warning", id="trust"),
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
