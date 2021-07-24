"""This view is used to create a new task"""
from typing import Optional

from prompt_toolkit import HTML
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import (
    HSplit, VSplit, Window, ConditionalContainer
)
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.validation import Validator
from prompt_toolkit.widgets import Box, Button, Frame, Label
from prompt_toolkit.filters import Condition

from python_kanban.models import Todo


class AddTaskView:
    HELP_TEXT = "Press `Tab` to move the focus"

    def __init__(self, app: Optional = None):
        self.app = app
        self.load_view()

    def load_view(self):

        title_row, title_buffer = self._get_title_row()
        body_row, body_buffer = self._get_body_row()

        add_button = Button(text="Add", handler=self._add)
        cancel_button = Button(text="Cancel", handler=self._cancel)
        buttons_row = Box(
            body=VSplit(
                [add_button, cancel_button], align="CENTER", padding=3
            ),
            style="class:button-bar",
            height=3,
        )
        help_text_row = Label(text=self.HELP_TEXT)

        self.focusable_elements = [
            title_buffer, body_buffer, add_button, cancel_button
        ]
        self.focused_element = 0
        self.task_inputs = [title_buffer, body_buffer]

        root_container = HSplit([title_row, body_row, buttons_row, help_text_row])

        self.layout = Layout(root_container)
        self._focus_on_element(0)

        return self.layout

    def _get_title_row(self):
        title_buffer = Buffer(
            validator=Validator.from_callable(_title_validator)
        )
        wrong_title = Condition(lambda: not title_buffer.validate())
        wrong_title_message = HTML(
            "<ansired>Title cannot be empty nor larger than "
            f"{Todo.title.max_length} characters</ansired>"
        )
        title_body = HSplit(
            [
                Window(content=BufferControl(buffer=title_buffer)),
                ConditionalContainer(
                    content=Label(wrong_title_message),
                    filter=wrong_title,
                ),
            ]
        )

        # Return the buffer as well since it needs to be stored in the focused
        # elements
        return Frame(title="Title*", body=title_body, height=5), title_buffer

    def _get_body_row(self):
        body_buffer = Buffer()

        return Frame(
            title="Description",
            body=Window(content=BufferControl(buffer=body_buffer)),
        ), body_buffer

    def _focus_on_element(self, index: int):
        self.layout.focus(self.focusable_elements[index])

    def load_key_bindings(self):
        kb = KeyBindings()

        @kb.add(Keys.Tab)
        def next_item(event) -> None:
            self.focused_element = (
                (self.focused_element + 1) % len(self.focusable_elements)
            )
            self._focus_on_element(self.focused_element)

        @kb.add(Keys.BackTab)
        def previous_item(event) -> None:
            self.focused_element = (
                (self.focused_element - 1) % len(self.focusable_elements)
            )
            self._focus_on_element(self.focused_element)

        return kb

    def _add(self):
        """Validate the inputs, save the Todo and load the list view"""
        for buffer_ in self.task_inputs:
            if not buffer_.validate():
                return

        # If everything is o.k., create a new Todo
        Todo.create(
            title=self.task_inputs[0].text, body=self.task_inputs[1].text
        )

        if self.app:
            self.app.load_list_tasks_view()

    def _cancel(self):
        """
        Main app should call `load_list_tasks_view` without creating anything
        """
        if self.app:
            self.app.load_list_tasks_view()


def _title_validator(text):
    return 0 < len(text) <= Todo.title.max_length
