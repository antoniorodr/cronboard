from __future__ import annotations

from textual.binding import Binding
from textual.widgets import RadioButton, RadioSet


class VimKeysRadioSet(RadioSet):
    """RadioSet with *j* / *k* keys."""

    BINDINGS = [
        Binding("j", "next_button", "Down"),
        Binding("k", "previous_button", "Up"),
    ]

    def action_next_button(self) -> None:
        super().action_next_button()
        self._apply_keyboard_selection()

    def action_previous_button(self) -> None:
        super().action_previous_button()
        self._apply_keyboard_selection()

    def _apply_keyboard_selection(self) -> None:
        if self._selected is None:
            return
        button = self._nodes[self._selected]
        if isinstance(button, RadioButton) and not button.value:
            button.value = True
