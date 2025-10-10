from textual.app import ComposeResult
from crontab import CronTab
from textual.widgets import Button, Label
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen


class CronDeleteConfirmation(ModalScreen[bool]):
    def __init__(self, job, cron=None, remote=False, ssh_client=None) -> None:
        super().__init__()
        self.job = job
        self.cron = cron if cron else CronTab(user=True)
        self.remote = remote
        self.ssh_client = ssh_client

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

        if self.remote and self.ssh_client:
            self.write_remote_crontab()
        else:
            self.cron.write()

        self.dismiss(True)

    def write_remote_crontab(self):
        """Writes the current SSH cron table back to the remote server."""
        if not (self.remote and self.ssh_client and self.cron):
            return False

        try:
            new_crontab_content = self.cron.render()

            stdin, _, stderr = self.ssh_client.exec_command("crontab -")
            stdin.write(new_crontab_content)
            stdin.channel.shutdown_write()

            exit_status = stdin.channel.recv_exit_status()
            errors = stderr.read().decode().strip()

            if errors:
                print(f"❌ Failed to write remote crontab: {errors}")
                return False

            if exit_status != 0:
                print(f"❌ Command failed with exit status: {exit_status}")
                return False

            print("✅ Remote crontab updated successfully")
            return True

        except Exception as e:
            print(f"❌ Error writing remote crontab: {e}")
            return False
