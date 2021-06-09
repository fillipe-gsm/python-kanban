"""Script to test my views visually"""
from prompt_toolkit.application import Application
from prompt_toolkit.shortcuts import message_dialog

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

    def raise_error_dialog(self, title: str, text: str):
        error_dialog = message_dialog(title=title, text=text)
        self.layout = error_dialog.layout


if __name__ == "__main__":
    application = TodoApplication()
    application.run()
