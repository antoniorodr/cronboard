from textual.app import ComposeResult
from crontab import CronTab
from textual.widgets import Button, Label, Input
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
import cronexpr
from cron_descriptor import Options, ExpressionDescriptor


class CronCreate(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Vertical(
                Label("Special characters:", id="label_special"),
                Label("* = any value", id="label_asterisk"),
                Label(", = value list separator", id="label_comma"),
                Label("- = range of values", id="label_dash"),
                Label("/ = step values", id="label_slash"),
                Label(
                    "Enter a valid cron expression (remember whitespaces):", id="label1"
                ),
                Label("Minute - Hour - Day - Month - Weekday", id="label2"),
                Input(placeholder="* * * * *", id="expression"),
                Label("", id="label_desc"),
                Label("Enter the command to execute:", id="label3"),
                Input(
                    placeholder="e.g., python3 /usr/bin/python</path/to/script.py>",
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

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "expression":
            return

        label_desc = self.query_one("#label_desc", Label)
        expr = event.value.strip()
        self.expression_description(expr, label_desc)

        error_labels = self.query("#error")
        for label in error_labels:
            label.remove()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "save":
            self.app.pop_screen()
            return

        expression_input = self.query_one("#expression", Input)
        command_input = self.query_one("#command", Input)
        expression = expression_input.value
        command = command_input.value

        content = self.query_one("#content", Vertical)

        try:
            cronexpr.next_fire(expression)

            cron = CronTab(user=True)
            cron_job = cron.new(command=command)
            cron_job.setall(expression)
            cron.write()

            self.app.pop_screen()

        except ValueError:
            if not self.query("#error"):
                error_label = Label(
                    "Invalid cron expression. Please try again.", id="error"
                )
                content.mount(error_label)

    def expression_description(self, expr: str, label_desc: Label) -> None:
        if not expr:
            label_desc.update("")
            label_desc.remove_class("success")
            label_desc.remove_class("error")
            return

        try:
            options = Options()
            options.locale_code = "en"
            options.use_24hour_time_format = True
            desc = ExpressionDescriptor(expr, options).get_description()

            label_desc.update(desc)
            label_desc.remove_class("error")
            label_desc.add_class("success")
        except Exception:
            label_desc.update("Invalid cron expression")
            label_desc.remove_class("success")
            label_desc.add_class("error")
