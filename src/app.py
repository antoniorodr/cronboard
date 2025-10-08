from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from widgets.Crontable import CronTable
from widgets.CronTabs import CronTabs
from widgets.CronCreate import CronCreate
from textual.binding import Binding


class CronBoard(App):
    """A Textual App to manage cron jobs."""

    CSS_PATH = "static/css/cronboard.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("j", "focus_next", "Down"),
        ("k", "focus_previous", "Up"),
        Binding("c", "create_cronjob_keybind", "Create cronjob", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield CronTabs("Local cronjobs", "SSH cronjobs")
        yield CronTable(id="crontable")

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"

    def action_create_cronjob_keybind(self) -> None:
        print("Create cronjob action triggered")
        self.push_screen(CronCreate())


if __name__ == "__main__":
    app = CronBoard()
    app.run()
