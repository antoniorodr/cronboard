from textual.app import ComposeResult
from crontab import CronTab
from textual.widgets import Button, Label, Input
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
import cronexpr


class CronCreate(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Vertical(
                Label("Enter a valid cron expression in this format:", id="label1"),
                Label("Minute - Hour - Day - Month - Weekday", id="label2"),
                Label("Special characters:", id="label_special"),
                Label("* = any value", id="label_asterisk"),
                Label(", = value list separator", id="label_comma"),
                Label("- = range of values", id="label_dash"),
                Label("/ = step values", id="label_slash"),
                Input(placeholder="* * * * *", id="expression"),
                Label("Enter the command to execute:", id="label3"),
                Input(
                    placeholder="e.g., /usr/bin/python</path/to/script.py>",
                    id="command",
                ),
                Horizontal(
                    Button("Save", variant="primary", id="save"),
                    Button("Cancel", variant="error", id="cancel"),
                    id="button-row",
                ),
                id="content",
            ),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            # Get the values from both inputs
            expression_input = self.query_one("#expression", Input)
            command_input = self.query_one("#command", Input)

            expression = expression_input.value
            command = command_input.value

            # TODO: Add validation and save logic here
            print(f"Expression: {expression}, Command: {command}")

            self.app.pop_screen()
        else:
            self.app.pop_screen()
