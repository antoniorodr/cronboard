from textual.app import ComposeResult
from textual.widgets import Button, Label, Input
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
import paramiko


class CronSSHModal(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Vertical(
                Label(
                    "Connect to a remote server via SSH to manage cron jobs",
                    id="label1",
                ),
                Input(
                    placeholder="Hostname (e.g. localhost:2222)",
                    id="hostname",
                ),
                Input(
                    placeholder="Username",
                    id="username",
                ),
                Input(
                    placeholder="Password",
                    id="password",
                ),
                Horizontal(
                    Button("Connect", variant="primary", id="connect"),
                    Button("Cancel", variant="error", id="cancel"),
                    id="button-row",
                ),
                id="content",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
            return

        if event.button.id == "connect":
            host_info = self.query_one("#hostname", Input).value.strip()
            username = self.query_one("#username", Input).value.strip()
            password = self.query_one("#password", Input).value.strip()

            try:
                hostname, port = host_info.split(":")
                port = int(port)
            except ValueError:
                print("Invalid host format. Use host:port")
                return

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(
                    hostname=hostname, port=port, username=username, password=password
                )
                stdin, stdout, stderr = client.exec_command("crontab -l")
                crontab_content = stdout.read().decode()
                self.dismiss(client)
            except paramiko.AuthenticationException:
                print("❌ Authentication failed")
                client.close()

            except Exception as e:
                print(f"❌ SSH error: {e}")
                client.close()
