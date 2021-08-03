"""This view is used to create a new task"""
from typing import Optional, TYPE_CHECKING

from prompt_toolkit import HTML
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import (
    focus_next, focus_previous
)
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import (
    HSplit, VSplit, Window, ConditionalContainer
)
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.validation import Validator
from prompt_toolkit.widgets import Box, Button, Frame, Label
from prompt_toolkit.filters import Condition

from python_kanban.models import Category, Todo


if TYPE_CHECKING:
    # Import here to prevent a circular import
    from python_kanban.app import KanbanApplication


class AddTaskView:
    HELP_TEXT = (
        "Press `Tab` to move the focus. "
        "Shortcut: Hit \"Esc\" to leave without doing anything."
    )

    def __init__(self, app: Optional["KanbanApplication"] = None):
        self.app = app
        self.load_view()

    def load_view(self):
        title_row = self._get_title_row()
        category_row = self._get_category_row()
        body_row = self._get_body_row()
        buttons_row = self._get_buttons_row()
        help_text_row = self._get_help_text_row()

        root_container = HSplit(
            [title_row, category_row, body_row, buttons_row, help_text_row]
        )

        self.layout = Layout(root_container, focused_element=title_row)

        return self.layout

    def _get_title_row(self):
        self.title_buffer = Buffer(
            validator=Validator.from_callable(_title_validator),
            multiline=False,
        )
        wrong_title_filter = Condition(
            lambda: not self.title_buffer.validate()
        )
        wrong_title_message = HTML(
            "<ansired>Title cannot be empty nor larger than "
            f"{Todo.title.max_length} characters</ansired>"
        )
        title_body = HSplit(
            [
                Window(content=BufferControl(buffer=self.title_buffer)),
                ConditionalContainer(
                    content=Label(wrong_title_message),
                    filter=wrong_title_filter,
                ),
            ]
        )

        return Frame(title="Title*", body=title_body, height=5)

    def _get_category_row(self):
        category_names = [
            category.name for category in Category.select(Category.name)
        ]
        category_completer = WordCompleter(category_names)
        self.category_buffer = Buffer(
            validator=Validator.from_callable(_category_validator),
            multiline=False,
            completer=category_completer,
            complete_while_typing=True,
        )
        wrong_category_filter = Condition(
            lambda: not self.category_buffer.validate()
        )
        wrong_category_message = HTML(
            "<ansired>Category cannot be larger than "
            f"{Category.name.max_length} characters</ansired>"
        )
        category_body = HSplit(
            [
                Window(content=BufferControl(buffer=self.category_buffer)),
                ConditionalContainer(
                    content=Label(wrong_category_message),
                    filter=wrong_category_filter,
                ),
            ]
        )

        return Frame(title="Category", body=category_body, height=5)

    def _get_body_row(self):
        self.body_buffer = Buffer()

        return Frame(
            title="Description",
            body=Window(content=BufferControl(buffer=self.body_buffer)),
        )

    def _get_buttons_row(self):
        add_button = Button(text="Add", handler=self._add)
        cancel_button = Button(text="Cancel", handler=self._cancel)

        return Box(
            body=VSplit(
                [add_button, cancel_button], align="CENTER", padding=3
            ),
            height=3,
        )

    def _get_help_text_row(self):
        return Label(text=self.HELP_TEXT)

    def load_key_bindings(self):
        """Use built-in functions to rotate between focusable elements."""
        kb = KeyBindings()
        kb.add("tab")(focus_next)
        kb.add("s-tab")(focus_previous)
        kb.add("escape")(lambda event: self._cancel())
        return kb

    def _add(self):
        """Validate the inputs, save the Todo and load the list view"""
        if not self._is_valid_form():
            return

        # If everything is o.k., create a new Todo
        Todo.create_todo_with_category(
            title=self.title_buffer.text,
            body=self.body_buffer.text,
            category_name=self.category_buffer.text,
        )

        if self.app:
            self.app.load_list_tasks_view()

    def _is_valid_form(self):
        """Return `True` if all required buffers are valid"""
        return self.title_buffer.validate() and self.category_buffer.validate()

    def _cancel(self):
        """
        Main app should call `load_list_tasks_view` without creating anything
        """
        if self.app:
            self.app.load_list_tasks_view()


def _title_validator(text):
    return 0 < len(text) <= Todo.title.max_length


def _category_validator(text):
    return len(text) <= Category.name.max_length
