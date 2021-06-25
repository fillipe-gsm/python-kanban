"""Main view where the user can see and manipulate existing tasks"""
from typing import Optional

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.widgets import Label

from python_kanban.models import Todo
from python_kanban.views.status_container_view import StatusContainer


class ListTasksView:
    def __init__(
        self,
        app: Optional = None,
        initial_container_focus: Optional[int] = None
    ):
        self.app = app
        self.load_view(initial_container_focus=initial_container_focus)

    def load_view(self, initial_container_focus: Optional[int] = None):
        """"""

        todo_entries_dict = Todo.group_todos_per_status()

        status_containers = [
            HSplit(
                [
                    Label(text=Todo.CHOICES[status][1]),
                    Window(height=1, char="_", style="class:line"),
                    StatusContainer(entries=todo_entries, app=self.app),
                ]
            )
            for status, todo_entries in todo_entries_dict.items()
        ]

        root_container = HSplit([
            VSplit(status_containers), Label(text="Press stuff")
        ])

        self.layout = Layout(root_container)
        self.status_containers = status_containers
        self.todo_entries_dict = todo_entries_dict

        # Set focus to a container
        if initial_container_focus:
            self.focused_element = initial_container_focus
            self._focus_on_element()
        else:
            self._focus_on_first_non_empty_container()

        return self.layout

    def _focus_on_element(self):
        self.layout.focus(self.status_containers[self.focused_element])

    def _focus_on_first_non_empty_container(self):
        """Traverse all status containers and focus on the first non-empty.
        Notice if there is no todo, this view should not be loaded anyway.
        """
        statuses = sorted(self.todo_entries_dict.keys())
        self.focused_element = next(
            (
                status for status in statuses if self.todo_entries_dict[status]
            )
        )
        self._focus_on_element()

    def load_key_bindings(self):
        kb = KeyBindings()
        statuses = sorted(self.todo_entries_dict.keys())

        @kb.add("a")
        def add_todo(event):
            if self.app:
                self.app.load_add_task_view()

        @kb.add("l")
        @kb.add(Keys.Right)
        def move_next_container(event):
            self.focused_element = next(
                (
                    status for status in statuses[self.focused_element + 1:]
                    if self.todo_entries_dict[status]
                ),
                self.focused_element
            )
            self._focus_on_element()

        @kb.add("h")
        @kb.add(Keys.Left)
        def move_previous_container(event):
            self.focused_element = next(
                (
                    status
                    for status in reversed(statuses[:self.focused_element])
                    if self.todo_entries_dict[status]
                ),
                self.focused_element
            )
            self._focus_on_element()

        @kb.add("q")
        def exit(event) -> None:
            if self.app:
                self.app.exit()

        return kb
