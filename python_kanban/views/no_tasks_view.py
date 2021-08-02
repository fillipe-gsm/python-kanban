"""This view is shown when there are no created tasks
It should contain simply a message indicating that there are no tasks and the
user should press "a" to add one.
"""

from typing import Optional, TYPE_CHECKING

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Box, Label


if TYPE_CHECKING:
    # Import here to prevent a circular import
    from python_kanban.app import KanbanApplication


class NoTasksView:
    MAIN_TEXT = "No tasks yet. Press \"a\" to add one or \"q\" to quit."

    def __init__(self, app: Optional["KanbanApplication"] = None):
        self.app = app
        self.load_view()

    def load_view(self):
        """Load main layout"""
        root_container = Box(
            body=Label(self.MAIN_TEXT, dont_extend_width=True),
        )
        self.layout = Layout(root_container)
        return self.layout

    def load_key_bindings(self):
        kb = KeyBindings()

        @kb.add("a")
        def add_task(event) -> None:
            if self.app:
                self.app.load_add_task_view()

        @kb.add("q")
        def exit(event) -> None:
            if self.app:
                self.app.exit()

        return kb
