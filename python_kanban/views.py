from typing import List, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Label

from python_kanban.models import Todo


class TodoContainer:
    def __init__(
        self, entries: List[Todo], app: Optional["TodoApplication"] = None
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


class TodoApplication(Application):
    def __init__(self):
        super().__init__(
            layout=self._list_view(),
            key_bindings=self._get_key_bindings(),
            full_screen=True,
        )
        self.current_focus = 0
        self._set_list_focus()

    def load_list_view(self):
        """Called to reload the list view"""
        self.layout = self._list_view()
        self._set_list_focus()

    def _set_list_focus(self):
        """
        In cases a window becomes empty after promoting or regressing too many
        todos, the focus should be shifted to the first with non-empty entries.
        If there is no entry at all, focus on the whole window.
        """

        if not self.todos_dict[self.current_focus]:
            self.current_focus = next(
                (i for i, todos in self.todos_dict.items() if todos), 0
            )

        self.layout.focus(self.windows[self.current_focus])

    def _list_view(self):
        """List view
        Shows all current todos grouped by statuses
        """

        todos_dict = Todo.group_todos_per_status()
        self.windows = [
            HSplit(
                [
                    Label(Todo.CHOICES[status][1]),
                    Window(height=1, char="-", style="class:line"),
                    TodoContainer(todos, app=self),
                ]
            )
            for status, todos in todos_dict.items()
        ]

        body = VSplit(self.windows)
        root_container = HSplit([body])
        self.todos_dict = todos_dict
        # return Layout(root_container, focused_element=self.windows[0])
        return Layout(root_container)

    def _get_key_bindings(self):
        # Global Key bindings
        kb = KeyBindings()

        @kb.add("q")
        def quit(event):
            """Quit application by pressing 'q'"""
            event.app.exit()

        @kb.add("l")
        @kb.add("right")
        def next(event):
            """Move to next window WITH non-empty todos"""
            self.current_focus = self._next_non_empty_window()
            event.app.layout.focus(self.windows[self.current_focus])

        @kb.add("h")
        @kb.add("left")
        def previous(event):
            """"""
            self.current_focus = self._previous_non_empty_window()
            event.app.layout.focus(self.windows[self.current_focus])

        return kb

    def _next_non_empty_window(self):
        for i in range(self.current_focus + 1, len(self.windows)):
            if self.todos_dict[i]:
                return i

        return self.current_focus

    def _previous_non_empty_window(self):
        for i in range(self.current_focus - 1, -1, -1):
            if self.todos_dict[i]:
                return i

        return self.current_focus


application = TodoApplication()
