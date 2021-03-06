from mock import Mock

from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys

from python_kanban.views.add_task_view import AddTaskView
from python_kanban.models import Category, Todo


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


def test_add_button_validation_proceeds_with_category():
    """The new todo must be created"""

    mocked_app = Mock()
    view = AddTaskView(app=mocked_app)

    assert Todo.select().count() == 0  # nothing on database yet
    assert Category.select().count() == 0  # nothing on database yet

    # Fill in some random task
    title = "Something to do"
    body = "Some details on what to do"
    category_name = "A category"
    view.title_buffer.text = title
    view.body_buffer.text = body
    view.category_buffer.text = category_name

    view._add()  # call the `add` button handler

    assert Todo.select().count() == 1  # the task was saved
    assert Category.select().count() == 1  # the category was saved
    todo = Todo.select()[0]
    assert todo.title == title
    assert todo.body == body
    assert todo.status == Todo.CHOICES[0][0]
    assert todo.category.name == category_name

    mocked_app.load_list_tasks_view.assert_called_once()


def test_add_button_validation_fails_with_invalid_category():
    """No todo is created"""

    view = AddTaskView()

    assert Todo.select().count() == 0  # nothing on database yet
    assert Category.select().count() == 0

    # Fill in some too large Category
    title = "Title"
    category_name = "Category" * Category.name.max_length
    view.title_buffer.text = title
    view.category_buffer.text = category_name

    view._add()  # call the `add` button handler

    assert Todo.select().count() == 0  # still nothing on database
    assert Category.select().count() == 0


def test_cancel_button():

    mocked_app = Mock()
    view = AddTaskView(app=mocked_app)

    view._cancel()  # call the `cancel` button handler

    mocked_app.load_list_tasks_view.assert_called_once()


def test_escape_cancels():
    mocked_app = Mock()
    view = AddTaskView(app=mocked_app)

    processor = KeyProcessor(view.load_key_bindings())
    processor.feed(KeyPress(Keys.Escape))
    processor.process_keys()

    mocked_app.load_list_tasks_view.assert_called_once()
