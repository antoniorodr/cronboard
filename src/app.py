import tomllib
import tomlkit
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Tabs
from widgets.CronTable import CronTable
from textual.containers import Container
from widgets.CronTabs import CronTabs
from widgets.CronCreator import CronCreator
from widgets.CronDeleteConfirmation import CronDeleteConfirmation
from widgets.CronSSHModal import CronSSHModal


class CronBoard(App):
    """A Textual App to manage cron jobs."""

    CSS_PATH = "static/css/cronboard.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("Tab", "focus_next", "Change Panel"),
    ]

    def compose(self) -> ComposeResult:
        version = self.get_version()
        self.config_path = Path.home() / ".config/cronboard/config.toml"
        yield Label(f"CronBoard v{version}", id="title")
        yield Footer()
        self.tabs = CronTabs("Local cronjobs", "SSH cronjobs")
        yield self.tabs
        self.content_container = Container(id="tab-content")
        yield self.content_container

    def on_mount(self) -> None:
        config = self.load_config()
        saved_theme = config.get("theme", "catppuccin-mocha")
        self.theme = saved_theme
        self.ssh_connected = False
        self.ssh_client = None
        self.ssh_table = None
        self.local_table = CronTable(id="local-crontable")
        self.content_container.mount(self.local_table)
        self.local_table.display = True

    def load_config(self):
        if self.config_path.exists():
            try:
                with self.config_path.open("rb") as f:
                    return tomllib.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
        return {}

    def watch_theme(self, theme: str):
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config_path.open("w") as f:
                f.write(tomlkit.dumps({"theme": theme}))
        except Exception as e:
            print(f"Warning: Failed to save theme: {e}")

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        tab_label = event.tab.label
        if tab_label == "Local cronjobs":
            self.show_tab_content(0)
        elif tab_label == "SSH cronjobs":
            if not self.ssh_connected:

                def on_ssh_connected(result):
                    if result:
                        self.ssh_client = result
                        self.ssh_connected = True
                        self.ssh_table = CronTable(
                            remote=True, ssh_client=self.ssh_client, id="ssh-crontable"
                        )
                        self.content_container.mount(self.ssh_table)
                        self.show_tab_content(1)
                    else:
                        self.ssh_connected = False

                self.push_screen(CronSSHModal(), on_ssh_connected)
            else:
                self.show_tab_content(1)

    def show_tab_content(self, index: int) -> None:
        if index == 0:
            self.local_table.display = True
            if self.ssh_table:
                self.ssh_table.display = False
        elif index == 1:
            self.local_table.display = False
            if self.ssh_table:
                self.ssh_table.display = True

    def action_ssh_connect(self) -> None:
        def check_connection(connected: bool | None) -> None:
            if connected:
                self.ssh_connected = True

        self.push_screen(CronSSHModal(), check_connection)

    def action_create_cronjob(self) -> None:
        def check_save(save: bool | None) -> None:
            if save:
                self.local_table.action_refresh()

        self.push_screen(CronCreator(), check_save)

    def action_delete_cronjob(self, job) -> None:
        def check_delete(deleted: bool | None) -> None:
            if deleted:
                self.local_table.action_refresh()

        self.push_screen(CronDeleteConfirmation(job), check_delete)

    def action_edit_cronjob(
        self, identificator: str, expression: str, command: str
    ) -> None:
        def check_save(save: bool | None) -> None:
            if save:
                self.local_table.action_refresh()

        self.push_screen(
            CronCreator(
                identificator=identificator, expression=expression, command=command
            ),
            check_save,
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
