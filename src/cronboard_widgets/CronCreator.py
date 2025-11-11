import os
from os import DirEntry
from pathlib import Path
from typing import Any, Callable

from textual.app import ComposeResult
from crontab import CronTab
from textual.widgets import Button, Label, Input
from textual.content import Content
from textual.cache import LRUCache
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual_autocomplete import AutoComplete, DropdownItem, PathAutoComplete, TargetState
from textual_autocomplete._path_autocomplete import PathDropdownItem, default_path_input_sort_key
from cron_descriptor import Options, ExpressionDescriptor


# TODO: Autocompletion using https://github.com/darrenburns/textual-autocomplete

CRON_ALIASES = {
    "@reboot": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@midnight": "0 0 * * *",
}

class CronAutoComplete(PathAutoComplete):
    def get_candidates(self, target_state: TargetState) -> list[DropdownItem]:
        """Get the candidates for the current path segment.

        This is called each time the input changes or the cursor position changes/
        """
        current_input_full = target_state.text[: target_state.cursor_position]
        # Hide Autocomplete when entering new command section
        if current_input_full.endswith(" "):
            return []
        # Get the last segment of the current full input
        current_input = current_input_full.split()[-1] if current_input_full else ""


        if "/" in current_input:
            last_slash_index = current_input.rindex("/")
            path_segment = current_input[:last_slash_index] or "/"
            directory = self.path / path_segment if path_segment != "/" else self.path
        else:
            directory = self.path

        # Use the directory path as the cache key
        cache_key = str(directory)
        cached_entries = self._directory_cache.get(cache_key)

        if cached_entries is not None:
            entries = cached_entries
        else:
            try:
                entries = list(os.scandir(directory))
                self._directory_cache[cache_key] = entries
            except OSError:
                return []

        results: list[PathDropdownItem] = []
        for entry in entries:
            # Only include the entry name, not the full path
            completion = entry.name
            if not self.show_dotfiles and completion.startswith("."):
                continue
            if entry.is_dir():
                completion += "/"
            results.append(PathDropdownItem(completion, path=Path(entry.path)))

        results.sort(key=self.sort_key)
        folder_prefix = self.folder_prefix
        file_prefix = self.file_prefix
        return [
            DropdownItem(
                item.main,
                prefix=folder_prefix if item.path.is_dir() else file_prefix,
            )
            for item in results
        ]

    def get_search_string(self, target_state: TargetState) -> str:
        """Return only the current path segment for searching in the dropdown."""
        current_input_full = target_state.text[: target_state.cursor_position].strip()
        # Get the last segment of the current full input
        current_input = current_input_full.split()[-1] if current_input_full else ""

        if "/" in current_input:
            last_slash_index = current_input.rindex("/")
            search_string = current_input[last_slash_index + 1 :]
            return search_string
        else:
            return current_input

    def apply_completion(self, value: str, state: TargetState) -> None:
        """Apply the completion by replacing only the current path segment."""
        def get_new_path_string(path_input: str, cursor_position: int):
        # There's a slash before the cursor, so we only want to replace
        # the text after the last slash with the selected value
            try:
                replace_start_index = path_input.rindex("/", 0, cursor_position)
            except ValueError:
                # No slashes, so we do a full replacement
                new_value = value
                new_cursor_position = len(value)
            else:
                # Keep everything before and including the slash before the cursor.
                path_prefix = path_input[: replace_start_index + 1]
                new_value = path_prefix + value
                new_cursor_position = len(path_prefix) + len(value)
            return new_value, new_cursor_position

        target = self.target
        current_input = state.text.strip()
        cursor_position = state.cursor_position

        # Get relevant space separated segment to complete, to keep other segments intact
        # e.g. "cp PATH_1 PATH_2" we must check which part to complete and keep the rest of the string

        string_before = ""
        string_after = ""
        first_split_index = 0
        # Just 2 parts
        if len(current_input.split()) == 2:
            first_split_index = current_input.index(" ")
            # completing the first part
            if cursor_position <= first_split_index+1:
                string_to_replace = current_input[:first_split_index]
                string_after = current_input[first_split_index+1:]
                new_value, new_cursor_position = get_new_path_string(path_input=string_to_replace, cursor_position=cursor_position)
            # completing the second part
            else:
                string_before = current_input[:first_split_index]
                string_to_replace = current_input[first_split_index+1:]
                new_value, new_cursor_position = get_new_path_string(path_input=string_to_replace, cursor_position=cursor_position)
                new_cursor_position += len(string_before) + 1
        
        # More than 2 parts
        elif len(current_input.split()) > 2:
            ...
            #TODO
        # Only 1 part to complete
        else:
            new_value, new_cursor_position = get_new_path_string(path_input=current_input, cursor_position=cursor_position)

        with self.prevent(Input.Changed):
            target.value = " ".join([part.strip() for part in [string_before, new_value, string_after] if part])
            target.cursor_position = new_cursor_position

    def post_completion(self) -> None:
        if not self.target.value.endswith("/"):
            self.action_hide()


class CronCreator(ModalScreen[bool]):
    def __init__(
        self,
        cron,
        expression=None,
        command=None,
        identificator=None,
        remote=False,
        ssh_client=None,
        crontab_user=None,
    ) -> None:
        super().__init__()
        self.expression = expression
        self.command = command
        self.identificator = identificator
        self.cron: CronTab = cron
        self.remote = remote
        self.ssh_client = ssh_client
        self.crontab_user = crontab_user

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            with Vertical(id="content"):
                yield Label("Special characters:", id="label_special")
                yield Label("* = any value", id="label_asterisk")
                yield Label(", = value list separator", id="label_comma")
                yield Label("- = range of values", id="label_dash")
                yield Label("/ = step values", id="label_slash")
                yield Label(
                    "Enter a valid cron expression (remember whitespaces):", id="label1"
                )
                yield Label("Minute - Hour - Day - Month - Weekday", id="label2")
                yield Input(
                    value="" if not self.expression else self.expression,
                    placeholder="* * * * *",
                    id="expression",
                )
                yield Label("", id="label_desc")
                yield Label("Enter the command to execute:", id="label3")
                command_input = Input(
                    value="" if self.command is None else self.command,
                    placeholder="e.g., python3 /usr/bin/python</path/to/script.py>",
                    id="command",
                )
                yield command_input
                yield CronAutoComplete(target=command_input)
                yield Label("Enter an ID for the cron job", id="label4")
                yield Input(
                    value="" if self.identificator is None else self.identificator,
                    placeholder="e.g., backup-job-1",
                    id="identificator",
                )
                yield Horizontal(
                    Button("Save", variant="primary", id="save"),
                    Button("Cancel", variant="error", id="cancel"),
                    id="button-row",
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
            error_label = Label("ID cannot be empty.", id="error")
            content.mount(error_label)
            return

        try:
            job = self.find_if_cronjob_exists(identificator, command)

            if job:
                job.set_command(command)
                job.setall(expression)
                self.write_cron_changes()
            else:
                cron_job = self.cron.new(command=command, comment=identificator)
                cron_job.setall(expression)
                self.write_cron_changes()

            self.dismiss(True)

        except (ValueError, KeyError):
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
            if expr == "@reboot":
                label_desc.update("Runs at system startup")
                label_desc.remove_class("error")
                label_desc.add_class("success")
                return

            expr = CRON_ALIASES.get(expr, expr)

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

    def write_cron_changes(self):
        """Write cron changes to appropriate destination (local or remote)"""
        if self.remote and self.ssh_client:
            try:
                new_crontab_content = self.cron.render()
                crontab_cmd = (
                    f"crontab -u {self.crontab_user} -"
                    if self.crontab_user
                    else "crontab -"
                )
                stdin, _, stderr = self.ssh_client.exec_command(crontab_cmd)
                stdin.write(new_crontab_content)
                stdin.channel.shutdown_write()

                exit_status = stdin.channel.recv_exit_status()
                errors = stderr.read().decode().strip()

                if errors or exit_status != 0:
                    self.notify(f"Failed to write remote crontab: {errors}")

            except Exception as e:
                print(f"❌ Error writing remote crontab: {e}")
                raise
        else:
            self.cron.write()

    def find_if_cronjob_exists(self, identificator: str, cmd: str):
        for job in self.cron:
            if job.comment == identificator and job.command == cmd:
                return job
        return None
