"""
View to see details and edit a task. It is similar to `AddTaskView`, but with
more info.
"""
from typing import Optional, TYPE_CHECKING

from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout.layout import Layout

from python_kanban.views.add_task_view import AddTaskView
from python_kanban.models import Todo
from prompt_toolkit.widgets import Box, Button, Label


if TYPE_CHECKING:
    # Import here to prevent a circular import
    from python_kanban.app import KanbanApplication


class EditTaskView(AddTaskView):
    def __init__(self, todo: Todo, app: Optional["KanbanApplication"] = None):
        self.app = app
        self.todo = todo
        self.load_view()

    def load_view(self):
        title_row = self._get_title_row()
        category_row = self._get_category_row()
        body_row = self._get_body_row()
        buttons_row = self._get_buttons_row()
        info_row = self._get_info_row()
        help_text_row = self._get_help_text_row()

        root_container = HSplit(
            [
                title_row,
                category_row,
                body_row,
                buttons_row,
                info_row,
                help_text_row
            ]
        )

        self.layout = Layout(root_container, focused_element=title_row)

        self._populate_fields()

        return self.layout

    def _get_buttons_row(self):
        add_button = Button(text="Save", handler=self._update)
        cancel_button = Button(text="Cancel", handler=self._cancel)

        return Box(
            body=VSplit(
                [add_button, cancel_button], align="CENTER", padding=3
            ),
            height=3,
        )

    def _get_info_row(self):
        """Return time info about the task"""
        created_at = Label(text=f"Created at {self.todo.created}")
        updated_at = Label(text=f"Last updated at {self.todo.updated}")
        return Box(
            body=VSplit(
                [created_at, updated_at], align="CENTER", padding=3
            ),
            height=3,
        )

    def _populate_fields(self):
        self.title_buffer.text = self.todo.title
        self.category_buffer.text = (
            self.todo.category.name
            if self.todo.category
            else ""
        )
        self.body_buffer.text = self.todo.body

    def _update(self):
        """Validate the inputs, save the edited Todo and load the list view"""
        if not self._is_valid_form():
            return

        # If everything is o.k., update the todo
        Todo.update_todo_with_category(
            todo=self.todo,
            title=self.title_buffer.text,
            body=self.body_buffer.text,
            category_name=self.category_buffer.text,
        )

        if self.app:
            self.app.load_list_tasks_view()
