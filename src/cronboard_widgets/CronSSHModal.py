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
                Label("AND", id="label_andor"),
                Input(
                    placeholder="Username",
                    id="username",
                ),
                Input(
                    placeholder="Password",
                    id="password",
                    password=True,
                ),
                Label("OR (Not yet implemented)", id="label_or"),
                Input(
                    placeholder="Private Key (e.g. /home/user/.ssh/id_rsa)",
                    id="privatekey",
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

    def on_input_changed(self, event: Input.Changed) -> None:
        if self.query("#error"):
            label_error = self.query_one("#error")
            label_error.remove()

        error_labels = self.query("#error")
        for label in error_labels:
            label.remove()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(False)
            return

        if event.button.id == "connect":
            host_info = self.query_one("#hostname", Input).value.strip()
            username = self.query_one("#username", Input).value.strip()
            password = self.query_one("#password", Input).value.strip()
            privatkey_path = self.query_one("#privatekey", Input).value.strip()
            content = self.query_one("#content", Vertical)

            try:
                hostname, port = host_info.split(":")
                port = int(port)
            except ValueError:
                if not self.query("#error"):
                    error_label = Label(
                        "Invalid host format. Use host:port", id="error"
                    )
                    content.mount(error_label)

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                if privatkey_path:
                    return
                    # private_key = paramiko.RSAKey.from_private_key_file(privatkey_path)
                    # client.connect(
                    #     hostname=hostname,
                    #     port=port,
                    #     username="root",
                    #     pkey=private_key,
                    # )
                else:
                    client.connect(
                        hostname=hostname,
                        port=port,
                        username=username,
                        password=password,
                    )

                self.dismiss(client)
            except paramiko.AuthenticationException:
                if not self.query("#error"):
                    error_label = Label("Authentication failed", id="error")
                    content.mount(error_label)
                client.close()

            except Exception as e:
                if not self.query("#error"):
                    error_label = Label("Authentication failed", id="error")
                    content.mount(error_label)
                client.close()
