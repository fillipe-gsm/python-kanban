from mock import Mock

from python_kanban.views.add_task_view import AddTaskView
from python_kanban.models import Todo


def test_add_button_validation_proceeds():
    """The new todo must be created"""

    mocked_app = Mock()
    view = AddTaskView(app=mocked_app)

    assert Todo.select().count() == 0  # nothing on database yet

    # Fill in some random task
    title = "Something to do"
    body = "Some details on what to do"
    view.title_buffer.text = title
    view.body_buffer.text = body

    view._add()  # call the `add` button handler

    assert Todo.select().count() == 1  # the task was saved
    todo = Todo.select()[0]
    assert todo.title == title
    assert todo.body == body
    assert todo.status == Todo.CHOICES[0][0]

    mocked_app.load_list_tasks_view.assert_called_once()


def test_add_button_validation_fails():
    """No todo is created"""

    view = AddTaskView()

    assert Todo.select().count() == 0  # nothing on database yet

    # Fill in some empty task
    title = ""
    body = ""
    view.title_buffer.text = title
    view.body_buffer.text = body

    view._add()  # call the `add` button handler

    assert Todo.select().count() == 0  # still nothing on database


def test_cancel_button():

    mocked_app = Mock()
    view = AddTaskView(app=mocked_app)

    view._cancel()  # call the `cancel` button handler

    mocked_app.load_list_tasks_view.assert_called_once()
