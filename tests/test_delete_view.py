import pytest

from python_kanban.views.delete_task_view import DeleteTaskView
from python_kanban.models import Todo


@pytest.fixture
def todo():
    return Todo.create(title="Task 1")


def test_delete_todo(todo):
    view = DeleteTaskView(todo=todo)

    assert Todo.select().count() == 1

    view._delete()

    assert Todo.select().count() == 0
