from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import ListView, ListItem, Label, Log, Button
from textual.message import Message
from textual import on
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from cronboard.services.logging.logger import get_log_files, read_log_file
from textual import events

class LogList(Widget):
    class LogSelected(Message):
        def __init__(self, log_path: str) -> None:
            self.log_path = log_path
            super().__init__()

    def __init__(self, identificator: str, ssh_client=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identificator = identificator
        self.log_paths = get_log_files(identificator, ssh_client)
        self.logs = list(self.log_paths.keys())

    def compose(self):
        yield ListView(
            *[ListItem(Label(log), id=log) for log in self.logs] if self.logs else [ListItem(Label("No logs found"), id="no_logs")],
        )

    def on_mount(self) -> None:
        for item in self.query(ListItem):
            item.styles.width = "100%"
        for label in self.query(Label):
            label.styles.width = "100%"
            label.styles.text_align = "left"

        for item in self.query(ListItem):
            item.styles.padding = (0, 0, 0, 1)

        if self.logs:
            first = self.logs[0]
            self.post_message(self.LogSelected(self.log_paths[first]))

    @on(ListView.Selected)
    def _on_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not item or not item.id or item.id == "no_logs":
            return

        path = self.log_paths[item.id]
        self.post_message(self.LogSelected(path))


class LogView(Widget):
    BINDINGS = [
        Binding("j", "jump", "Switch Panel"),
    ]

    def __init__(self, identificator: str, ssh_client=None) -> None:
        super().__init__()
        self.ssh_client = ssh_client
        self.log_list = LogList(identificator=identificator, id="log-list", ssh_client=ssh_client)
        self.log_output = Log(classes="focusable")

    def compose(self) -> ComposeResult:
        with Vertical(id="content"):
            yield Horizontal(
                self.log_list,
                self.log_output,
                id="main",
            )
            yield Horizontal(
                Button("Close", variant="error", id="close"),
                id="button-row",
            )
        
        self.log_output.styles.width = "70%"
        self.log_list.styles.width = "30%"

    def on_mount(self) -> None:
        self.app.disable_tab()
        self.log_output.write_line("Please select a log from the list on the left.")

    def on_key(self, event: events.Key) -> None:
        if event.key == "tab":
            if isinstance(self.app.focused, ListView):
                self.app.set_focus(self.log_output)
            elif self.log_output.has_focus:
                self.query_one("#close", Button).focus()
            else:
                self.app.set_focus(self.log_list.query_one(ListView))

    @on(LogList.LogSelected)
    def show_log(self, event: LogList.LogSelected):
        self.log_output.clear()

        for line in read_log_file(event.log_path, self.ssh_client):
            self.log_output.write_line(line)



class LogViewModal(ModalScreen[bool]):  
    def __init__(self, identificator: str, ssh_client=None):
        super().__init__()
        self.identificator = identificator
        self.ssh_client = ssh_client
    def compose(self) -> ComposeResult:
        dialog = Grid(
            LogView(identificator=self.identificator, ssh_client=self.ssh_client),
            id="dialog",
        )

        dialog.styles.width = "90%"
        dialog.styles.height = "85%"
        yield dialog

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.enable_tab()
        self.dismiss(True)