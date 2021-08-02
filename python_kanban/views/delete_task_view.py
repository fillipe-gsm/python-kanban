"""This view is used to delete a new task"""
from typing import Optional, TYPE_CHECKING

from prompt_toolkit.widgets import Box, Button, Label
from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.layout import Layout

from python_kanban.models import Todo
from python_kanban.views.add_task_view import AddTaskView


if TYPE_CHECKING:
    # Import here to prevent a circular import
    from python_kanban.app import KanbanApplication


class DeleteTaskView(AddTaskView):
    HELP_TEXT = (
        "Press `Tab` to move the focus. "
        "Shortcut: Hit \"Esc\" to leave without deleting the task."
    )

    def __init__(self, todo: Todo, app: Optional["KanbanApplication"] = None):
        self.app = app
        self.todo = todo
        self.load_view()

    def load_view(self):
        message_row = self._get_message_row()
        buttons_row = self._get_buttons_row()
        help_text_row = self._get_help_text_row()

        root_container = HSplit(
            [message_row, buttons_row, help_text_row]
        )

        self.layout = Layout(root_container, focused_element=buttons_row)

        return self.layout

    def _get_message_row(self):
        dialog_text = Label(text="Are you sure you want to delete:")
        todo_text = Label(text=f"\"{self.todo.title}\"?")

        return Box(
            body=HSplit(
                [dialog_text, todo_text], align="CENTER", padding=3
            )
        )

    def _get_buttons_row(self):
        delete_button = Button(text="Delete", handler=self._delete)
        cancel_button = Button(text="Cancel", handler=self._cancel)

        return Box(
            body=VSplit(
                [delete_button, cancel_button], align="CENTER", padding=3
            ),
            height=3,
        )

    def _delete(self):
        self.todo.delete_instance()
        if self.app:
            self.app.load_list_tasks_view()
