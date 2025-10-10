from textual.app import ComposeResult
from crontab import CronTab
from textual.widgets import Button, Label, Input
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
import cronexpr
from cron_descriptor import Options, ExpressionDescriptor


class CronCreator(ModalScreen[bool]):
    def __init__(self, expression=None, command=None, identificator=None) -> None:
        super().__init__()
        self.expression = expression
        self.command = command
        self.identificator = identificator
        self.cron = CronTab(user=True)

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
                Input(
                    value="" if not self.expression else self.expression,
                    placeholder="* * * * *",
                    id="expression",
                ),
                Label("", id="label_desc"),
                Label("Enter the command to execute:", id="label3"),
                Input(
                    value="" if self.command is None else self.command,
                    placeholder="e.g., python3 /usr/bin/python</path/to/script.py>",
                    id="command",
                ),
                Label("Enter a identificator", id="label4"),
                Input(
                    value="" if self.identificator is None else self.identificator,
                    placeholder="e.g., backup-job-1",
                    id="identificator",
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
            self.dismiss(False)
            return

        identificator_input = self.query_one("#identificator", Input)
        expression_input = self.query_one("#expression", Input)
        command_input = self.query_one("#command", Input)
        expression = expression_input.value
        command = command_input.value
        identificator = identificator_input.value
        content = self.query_one("#content", Vertical)

        if not identificator:
            error_label = Label("Identificator cannot be empty.", id="error")
            content.mount(error_label)
            return

        try:
            cronexpr.next_fire(expression)

            cron = self.cron
            job = self.find_if_cronjob_exists(identificator, command)

            if job:
                job.set_command(command)
                job.setall(expression)
                cron.write()
            else:
                cron_job = cron.new(command=command, comment=identificator)
                cron_job.setall(expression)
                cron.write()

            self.dismiss(True)

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

    def find_if_cronjob_exists(self, identificator: str, cmd: str):
        for job in self.cron:
            if job.comment == identificator and job.command == cmd:
                return job
        return None
