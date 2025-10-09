from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Tabs
from widgets.CronTable import CronTable
from textual.containers import Container
from widgets.CronTabs import CronTabs
from widgets.CronCreator import CronCreator


class CronBoard(App):
    """A Textual App to manage cron jobs."""

    CSS_PATH = "static/css/cronboard.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("Tab", "focus_next", "Change Panel"),
    ]

    def compose(self) -> ComposeResult:
        version = self.get_version()
        yield Label(f"CronBoard v{version}", id="title")
        yield Footer()
        self.tabs = CronTabs("Local cronjobs", "SSH cronjobs")
        yield self.tabs
        self.content_container = Container(id="tab-content")
        yield self.content_container

    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"

        self.local_table = CronTable(id="local-crontable")
        self.ssh = Label("SSH cronjobs view (not implemented)", id="ssh-placeholder")

        self.content_container.mount(self.local_table)
        self.content_container.mount(self.ssh)

        self.local_table.display = True
        self.ssh.display = False

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        tab_label = event.tab.label
        if tab_label == "Local cronjobs":
            self.show_tab_content(0)
        elif tab_label == "SSH cronjobs":
            self.show_tab_content(1)

    def show_tab_content(self, index: int) -> None:
        if index == 0:
            self.local_table.display = True
            self.ssh.display = False
        elif index == 1:
            self.local_table.display = False
            self.ssh.display = True

    def action_create_cronjob_keybind(self) -> None:
        self.push_screen(CronCreator())

    def action_edit_cronjob_keybind(
        self, identificator: str, expression: str, command: str
    ) -> None:
        self.push_screen(
            CronCreator(
                identificator=identificator, expression=expression, command=command
            )
        )

    def get_version(self) -> str:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        try:
            with pyproject_path.open("r") as f:
                for line in f:
                    if line.startswith("version"):
                        return line.split("=")[1].strip().replace('"', "")
        except FileNotFoundError:
            return "Unknown version"
        return "Unknown version"


def main():
    app = CronBoard()
    app.run()


if __name__ == "__main__":
    app = CronBoard()
    app.run()
