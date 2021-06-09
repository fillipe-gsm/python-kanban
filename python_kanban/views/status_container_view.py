"""
Contains the main view showing all todos by status, in which the user can
navigate, promote, regress and delete the tasks.
"""
from typing import List, Optional

from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl


from python_kanban.models import Todo


class StatusContainer:
    """A widget-like container for the todos with a given status"""

    def __init__(
        self, entries: List[Todo], app: Optional = None
    ):
        self.entries = entries
        self.selected_line = 0
        self.container = Window(
            content=FormattedTextControl(
                text=self._get_formatted_text,
                focusable=True,
                key_bindings=self._get_key_bindings(),
            ),
            style="class:select-box",
            dont_extend_height=True,
            cursorline=True,
        )
        self.app = app

    def _get_formatted_text(self):
        result = []
        for i, entry in enumerate(self.entries):
            if i == self.selected_line:
                result.append([("[SetCursorPosition]", "")])
            result.append(entry.title)
            result.append("\n")

        return merge_formatted_text(result)

    def _get_key_bindings(self):
        kb = KeyBindings()

        @kb.add("k")
        @kb.add("up")
        def _go_up(event) -> None:
            self.selected_line = (self.selected_line - 1) % len(self.entries)

        @kb.add("j")
        @kb.add("down")
        def _go_down(event) -> None:
            self.selected_line = (self.selected_line + 1) % len(self.entries)

        @kb.add("p")
        def _promote(event) -> None:
            self.entries[self.selected_line].promote()
            if self.app:
                self.app.load_list_view()

        @kb.add("r")
        def _regress(event) -> None:
            self.entries[self.selected_line].regress()
            if self.app:
                self.app.load_list_view()

        return kb

    def __pt_container__(self):
        return self.container
