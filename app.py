"""Script to test my views visually"""
from typing import Optional

from prompt_toolkit.application import Application

from python_kanban.views.add_task_view import AddTaskView
from python_kanban.views.list_tasks_view import ListTasksView


class TodoApplication(Application):
    def __init__(self):
        # view = AddTaskView(app=self)
        # super().__init__(
            # layout=view.load_view(),
            # key_bindings=view.load_key_bindings(),
            # full_screen=True
        # )
        view = ListTasksView(app=self)
        super().__init__(
            layout=view.load_view(),
            key_bindings=view.load_key_bindings(),
            full_screen=True,
        )

    def load_add_task_view(self):
        self.exit()

    def load_list_tasks_view(
        self, initial_container_focus: Optional[int] = None
    ):
        view = ListTasksView(
            app=self, initial_container_focus=initial_container_focus
        )
        self.layout = view.layout
        self.key_bindings = view.load_key_bindings()


if __name__ == "__main__":
    application = TodoApplication()
    application.run()
