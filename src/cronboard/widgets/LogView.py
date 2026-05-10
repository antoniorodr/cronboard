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

    def _post_log_for_item(self, item: ListItem | None) -> None:
        if not item or not item.id or item.id == "no_logs":
            return
        self.post_message(self.LogSelected(self.log_paths[item.id]))

    @on(ListView.Highlighted)
    def _on_highlighted(self, event: ListView.Highlighted) -> None:
        """Cursor up/down changes highlight; load that log in the right pane."""
        self._post_log_for_item(event.item)

    @on(ListView.Selected)
    def _on_selected(self, event: ListView.Selected) -> None:
        """Enter confirms selection (same path as highlight when using keyboard)."""
        self._post_log_for_item(event.item)


class LogView(Widget):
    BINDINGS = [
        Binding("l", "cursor_right", "Right"),
        Binding("h", "cursor_left", "Left"),
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
    ]

    def __init__(self, identificator: str, ssh_client=None) -> None:
        super().__init__()
        self.ssh_client = ssh_client
        self.log_list = LogList(identificator=identificator, id="log-list", ssh_client=ssh_client)
        self.log_output = Log(classes="focusable")

    def _list_view(self) -> ListView:
        return self.log_list.query_one(ListView)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        is_empty = not self.log_list.logs
        if action in (
            "cursor_up",
            "cursor_down",
            "cursor_left",
            "cursor_right",
        ):
            return not is_empty
        return True

    def action_cursor_left(self) -> None:
        self.app.set_focus(self._list_view())

    def action_cursor_right(self) -> None:
        self.app.set_focus(self.log_output)

    def action_cursor_down(self) -> None:
        if self.log_output.has_focus:
            self.log_output.action_scroll_down()
            return
        if self.log_list.has_focus_within:
            self._list_view().action_cursor_down()

    def action_cursor_up(self) -> None:
        if self.log_output.has_focus:
            self.log_output.action_scroll_up()
            return
        if self.log_list.has_focus_within:
            self._list_view().action_cursor_up()

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
        lines = read_log_file(event.log_path, self.ssh_client)
        if len(lines) == 0:
            self.log_output.write_line("No logs found")
        for line in lines:
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