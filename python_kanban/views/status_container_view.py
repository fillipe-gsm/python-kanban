"""
"""
from typing import List, Optional, TYPE_CHECKING

from prompt_toolkit import HTML
from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl


from python_kanban.models import Todo


if TYPE_CHECKING:
    # Import here to prevent a circular import
    from python_kanban.app import KanbanApplication


class StatusContainer:
    """A widget-like container for the todos with a given status"""

    def __init__(
        self, entries: List[Todo], app: Optional["KanbanApplication"] = None
    ):
        self.entries = entries
        self.selected_line = 0
        self.container = Window(
            content=FormattedTextControl(
                text=self._get_formatted_text,
                focusable=True,
                key_bindings=self._get_key_bindings(),
            ),
            cursorline=True,
        )
        self.app = app

    def _get_formatted_text(self):
        result = []
        for i, entry in enumerate(self.entries):
            if i == self.selected_line:
                result.append([("[SetCursorPosition]", "")])

            category_name = HTML(
                f"[<bold>{entry.category.name}</bold>] "
                if entry.category
                else ""
            )
            result.append(category_name)
            result.append(entry.title)
            result.append("\n")

        return merge_formatted_text(result)

    def _get_key_bindings(self):  # noqa
        """
        Set #noqa to prevent flake8 from calling this function 'too complex'.
        It should actually contain all keybindings here.
        """
        kb = KeyBindings()

        @kb.add("k")
        @kb.add("up")
        def go_up(event):
            self.selected_line = (self.selected_line - 1) % len(self.entries)

        @kb.add("j")
        @kb.add("down")
        def go_down(event):
            self.selected_line = (self.selected_line + 1) % len(self.entries)

        @kb.add("p")
        def promote(event):
            todo = self.entries[self.selected_line]
            todo.promote()
            if self.app:
                self.app.load_list_tasks_view(
                    initial_container_focus=todo.status
                )

        @kb.add("r")
        def regress(event):
            todo = self.entries[self.selected_line]
            todo.regress()
            if self.app:
                self.app.load_list_tasks_view(
                    initial_container_focus=todo.status
                )

        @kb.add("d")
        def delete(event):
            todo = self.entries[self.selected_line]
            if self.app:
                self.app.load_delete_task_view(todo=todo)

        @kb.add("e")
        def edit_todo(event):
            todo = self.entries[self.selected_line]
            if self.app:
                self.app.load_edit_task_view(todo=todo)

        return kb

    def __pt_container__(self):
        return self.container
