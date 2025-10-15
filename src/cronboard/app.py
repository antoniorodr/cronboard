import tomllib
from importlib.metadata import version, PackageNotFoundError
from crontab import CronTab
import tomlkit
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Tabs, Tab
from cronboard_widgets.CronTable import CronTable
from textual.containers import Container
from cronboard_widgets.CronTabs import CronTabs
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation
from cronboard_widgets.ServersBookmarkScreen import ServersBookmarkScreen
import paramiko


class CronBoard(App):
    """A Textual App to manage cron jobs."""

    BASE_DIR = Path(__file__).resolve().parent
    CSS_PATH = BASE_DIR / "static" / "css" / "cronboard.tcss"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("Tab", "focus_next", "Change Panel"),
    ]

    # Define tab IDs and labels as class constants for consistency and clarity
    LOCAL_TAB_ID = "local"
    SSH_TAB_ID = "ssh"
    LOCAL_TAB_LABEL = "Local cronjobs"
    SSH_TAB_LABEL = "SSH cronjobs"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        app_version = self.get_version()
        self.config_path = Path.home() / ".config/cronboard/config.toml"
        yield Label(f"CronBoard v{app_version}", id="title")
        yield Footer()
        self.tabs = CronTabs(
            Tab(self.LOCAL_TAB_LABEL, id=self.LOCAL_TAB_ID),
            Tab(self.SSH_TAB_LABEL, id=self.SSH_TAB_ID),
        )
        yield self.tabs
        self.content_container = Container(id="tab-content")
        yield self.content_container

    def on_mount(self) -> None:
        """Called after the app is mounted."""
        config = self.load_config()
        self.theme = config.get("theme", "catppuccin-mocha")
        self.server_bookmarks: list[dict] = config.get("servers", [])
        self.ssh_connected: bool = False
        self.ssh_client: paramiko.SSHClient | None = None
        self.ssh_table: CronTable | None = None
        self.local_table = CronTable(id="local-crontable")
        self.content_container.mount(self.local_table)
        self.local_table.display = True

    def load_config(self) -> dict:
        """Loads configuration from config.toml."""
        if self.config_path.exists():
            try:
                with self.config_path.open("rb") as f:
                    return tomllib.load(f)
            except Exception as e:
                # Use self.log for internal app messages, visible via textual console
                self.log(f"Warning: Failed to load config from {self.config_path}: {e}")
        return {}

    def save_config(self) -> None:
        """Saves current configuration (theme and server bookmarks) to config.toml."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        config_data = {
            "theme": self.theme,
            "servers": self.server_bookmarks,
        }
        try:
            with self.config_path.open("w") as f:
                tomlkit.dump(config_data, f)
        except Exception as e:
            self.log(f"Warning: Failed to save config to {self.config_path}: {e}")

    def watch_theme(self, theme: str) -> None:
        """Watches for changes in the theme and saves the configuration."""
        self.theme = theme
        self.save_config()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handles tab activation events."""
        tab_label = event.tab.label
        if tab_label == self.LOCAL_TAB_LABEL:
            self.show_tab_content(0)
        elif tab_label == self.SSH_TAB_LABEL:
            if not self.ssh_connected:

                def on_server_connected(result: paramiko.SSHClient | None) -> None:
                    """Callback for when a server connection attempt finishes."""
                    if result is not None:
                        self.ssh_client = result
                        self.ssh_connected = True
                        self.ssh_table = CronTable(
                            remote=True, ssh_client=self.ssh_client, id="ssh-crontable"
                        )
                        self.content_container.mount(self.ssh_table)
                        self.show_tab_content(1)
                    else:
                        # Connection failed or user canceled, switch back to local
                        self.ssh_connected = False
                        self.tabs.active = self.LOCAL_TAB_ID
                        self.show_tab_content(0)

                self.push_screen(
                    ServersBookmarkScreen(self.server_bookmarks, self.save_config),
                    on_server_connected,
                )
            else:
                self.show_tab_content(1)

    def show_tab_content(self, index: int) -> None:
        """Displays the content for the selected tab index."""
        if index == 0:  # Local cronjobs tab
            self.local_table.display = True
            if self.ssh_table:
                self.ssh_table.display = False
        elif index == 1:  # SSH cronjobs tab
            self.local_table.display = False
            if self.ssh_table:
                self.ssh_table.display = True

    def action_disconnect_ssh(self) -> None:
        """Disconnects the current SSH connection and returns to the local cron tab."""
        if self.ssh_client:
            try:
                self.ssh_client.close()
                self.log("✅ SSH client closed.")
            except Exception as e:
                self.log(f"Warning: Error closing SSH connection: {e}")

        self.ssh_client = None
        self.ssh_connected = False

        if self.ssh_table:
            # Explicitly remove the widget from the DOM
            self.ssh_table.remove()
            self.ssh_table = None

        self.tabs.active = self.LOCAL_TAB_ID
        self.show_tab_content(0)

    def action_create_cronjob(
        self, cron: CronTab, remote: bool = False, ssh_client: paramiko.SSHClient | None = None
    ) -> None:
        """Pushes the CronCreator screen for creating a new cron job."""
        def check_save(save: bool | None) -> None:
            """Callback after CronCreator screen is dismissed."""
            if save:
                self.local_table.action_refresh()
                if self.ssh_table:
                    self.ssh_table.action_refresh()

        self.push_screen(
            CronCreator(cron, remote=remote, ssh_client=ssh_client), check_save
        )

    def action_delete_cronjob(
        self, job, cron: CronTab | None = None, remote: bool = False, ssh_client: paramiko.SSHClient | None = None
    ) -> None:
        """Pushes the CronDeleteConfirmation screen for deleting a cron job."""
        def check_delete(deleted: bool | None) -> None:
            """Callback after CronDeleteConfirmation screen is dismissed."""
            if deleted:
                self.local_table.action_refresh()
                if self.ssh_table:
                    self.ssh_table.action_refresh()

        self.push_screen(
            CronDeleteConfirmation(
                job, cron=cron, remote=remote, ssh_client=ssh_client
            ),
            check_delete,
        )

    def action_edit_cronjob(
        self,
        cron: CronTab,
        identificator: str,
        expression: str,
        command: str,
        remote: bool = False,
        ssh_client: paramiko.SSHClient | None = None,
    ) -> None:
        """Pushes the CronCreator screen for editing an existing cron job."""
        def check_save(save: bool | None) -> None:
            """Callback after CronCreator screen is dismissed."""
            if save:
                self.local_table.action_refresh()
                if self.ssh_table:
                    self.ssh_table.action_refresh()

        self.push_screen(
            CronCreator(
                cron,
                identificator=identificator,
                expression=expression,
                command=command,
                remote=remote,
                ssh_client=ssh_client,
            ),
            check_save,
        )

    def get_version(self) -> str:
        """Retrieves the package version from metadata."""
        try:
            return version("cronboard")
        except PackageNotFoundError:
            return "Unknown"


def main() -> None:
    """Main entry point for the CronBoard application."""
    app = CronBoard()
    app.run()


if __name__ == "__main__":
    main()