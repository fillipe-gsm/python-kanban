from typing import List

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import HTML, merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Label

from python_kanban.models import Todo


class TodoContainer:
    def __init__(self, entries: List[Todo]):
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
            # TODO: add the real app and reload everything

        @kb.add("r")
        def _regress(event) -> None:
            self.entries[self.selected_line].regress()

        return kb

    def __pt_container__(self):
        return self.container


class UserInterface:
    def __init__(self):

        # Layout
        todo_list = [
            HTML("<bold>Task 1</bold> Dar o cu"),
            HTML("<bold>Task 2</bold> Dar o cu"),
            HTML("<bold>Task 3</bold> Dar o cu"),
        ]
        todo_window = HSplit([
            Label("To do"),
            Window(height=1, char="-", style="class:line"),
            TodoContainer(todo_list),
        ])
        inprogress_window = HSplit([
            Label("In progress"),
            Window(height=1, char="-", style="class:line"),
            TodoContainer(todo_list),
        ])
        done_window = HSplit([
            Label("Done"),
            Window(height=1, char="-", style="class:line"),
            TodoContainer(todo_list),
        ])

        self.windows = [
            todo_window,
            inprogress_window,
            done_window,
        ]

        body = VSplit(self.windows)
        self.root_container = HSplit([body])
        self.current_focus = 0
        self._set_key_bindings()

    def _set_key_bindings(self):
        # Global Key bindings
        kb = KeyBindings()

        @kb.add("q")
        def quit(event):
            """Quit application by pressing 'q'"""
            event.app.exit()

        @kb.add("l")
        @kb.add("right")
        def next(event):
            """"""
            self.current_focus = min(
                len(self.windows) - 1, self.current_focus + 1
            )
            event.app.layout.focus(self.windows[self.current_focus])

        @kb.add("h")
        @kb.add("left")
        def previous(event):
            """"""
            self.current_focus = max(0, self.current_focus - 1)
            event.app.layout.focus(self.windows[self.current_focus])

        self.kb = kb


interface = UserInterface()

# Glues the whole app
application = Application(
    layout=Layout(
        interface.root_container, focused_element=interface.windows[0]
    ),
    key_bindings=interface.kb,
    full_screen=True,
)
