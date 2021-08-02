"""Main app with the Kanban functionality"""
from typing import Optional

from prompt_toolkit.application import Application

from python_kanban.models import Category, Todo
from python_kanban.views.no_tasks_view import NoTasksView
from python_kanban.views.add_task_view import AddTaskView
from python_kanban.views.edit_tasks_view import EditTaskView
from python_kanban.views.delete_task_view import DeleteTaskView
from python_kanban.views.list_tasks_view import ListTasksView


class KanbanApplication(Application):
    """
    The main idea of the app is to change layouts depending on the functions
    called by internal views.
    """

    def __init__(self):
        view = (
            ListTasksView(app=self)
            if Todo.select().count()
            else NoTasksView(app=self)
        )
        super().__init__(
            layout=view.load_view(),
            key_bindings=view.load_key_bindings(),
            full_screen=True,
        )

    def load_add_task_view(self):
        view = AddTaskView(app=self)
        self.layout = view.layout
        self.key_bindings = view.load_key_bindings()

    def load_edit_task_view(self, todo: Todo):
        view = EditTaskView(app=self, todo=todo)
        self.layout = view.layout
        self.key_bindings = view.load_key_bindings()

    def load_list_tasks_view(
        self, initial_container_focus: Optional[int] = None
    ):
        view = (
            ListTasksView(
                app=self, initial_container_focus=initial_container_focus
            )
            if Todo.select().count()
            else NoTasksView(app=self)
        )

        # FIXME: Mypy went nuts here and said `view` has not `layout` nor
        # `load_key_bindings`, which is clearly wrong. I looked everywhere but
        # found no solution, so I'll simply ask it to ignore it for now
        self.layout = view.layout  # type: ignore
        self.key_bindings = view.load_key_bindings()  # type: ignore

    def load_delete_task_view(self, todo=Todo):
        view = DeleteTaskView(app=self, todo=todo)
        self.layout = view.layout
        self.key_bindings = view.load_key_bindings()


def run_app():
    from python_kanban.models import db

    db.create_tables([Category, Todo])
    application = KanbanApplication()
    application.run()
