"""Script to test my views visually"""
from prompt_toolkit.application import Application

from python_kanban.views.add_task_view import AddTaskView


class TodoApplication(Application):
    def __init__(self):
        view = AddTaskView(app=self)
        super().__init__(
            layout=view.load_view(),
            key_bindings=view.load_key_bindings(),
            full_screen=True
        )

    def load_add_task_view(self):
        self.exit()


if __name__ == "__main__":
    application = TodoApplication()
    application.run()
