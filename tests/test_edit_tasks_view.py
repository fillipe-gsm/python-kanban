import pytest

from python_kanban.views.edit_tasks_view import EditTaskView
from python_kanban.models import Todo


@pytest.fixture
def todo():
    return Todo.create(
        title="Todo Title", body="Todo Body", status=Todo.CHOICES[0][0]
    )


def test_fields_are_populated(todo):
    view = EditTaskView(todo=todo)

    assert view.title_buffer.text == todo.title
    assert view.body_buffer.text == todo.body


def test_todo_is_edited(todo):
    view = EditTaskView(todo=todo)

    new_title = "Updated Todo Title"
    view.title_buffer.text = new_title
    view._update()

    assert view.title_buffer.text == new_title
