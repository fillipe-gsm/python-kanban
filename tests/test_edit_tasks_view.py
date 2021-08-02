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

    updated_todo = Todo.select()[0]
    assert updated_todo.title == new_title


def test_todo_with_new_category_is_edited(todo):
    view = EditTaskView(todo=todo)

    new_category_name = "Now a category"
    view.category_buffer.text = new_category_name
    view._update()

    updated_todo = Todo.select()[0]
    assert updated_todo.category.name == new_category_name
