from mock import Mock
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys

from python_kanban.views.add_task_view import AddTaskView
from python_kanban.models import Todo


def test_tab_should_focus_on_next_element():
    view = AddTaskView()

    assert view.focused_element == 0
    assert view.layout.has_focus(view.focusable_elements[0])

    processor = KeyProcessor(view.load_key_bindings())

    processor.feed(KeyPress(Keys.Tab))
    processor.process_keys()

    assert view.focused_element == 1
    assert view.layout.has_focus(view.focusable_elements[1])


def test_backtab_should_focus_on_previous_element():
    view = AddTaskView()

    assert view.focused_element == 0
    assert view.layout.has_focus(view.focusable_elements[0])

    processor = KeyProcessor(view.load_key_bindings())

    processor.feed(KeyPress(Keys.BackTab))
    processor.process_keys()

    new_index = len(view.focusable_elements) - 1
    assert view.focused_element == new_index
    assert view.layout.has_focus(view.focusable_elements[new_index])


def test_add_button_validation_proceeds():
    """The new todo must be created"""

    mocked_app = Mock()
    view = AddTaskView(app=mocked_app)

    assert Todo.select().count() == 0  # nothing on database yet

    # Fill in some random task
    title = "Something to do"
    body = "Some details on what to do"
    view.task_inputs[0].text = title
    view.task_inputs[1].text = body

    # Get the add button and simulate a press
    add_button = next(
        (
            element for element in view.focusable_elements
            if element.text == "Add"
        )
    )
    add_button.handler()

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
    view.task_inputs[0].text = title
    view.task_inputs[1].text = body

    # Get the add button and simulate a press
    add_button = next(
        (
            element for element in view.focusable_elements
            if element.text == "Add"
        )
    )
    add_button.handler()

    assert Todo.select().count() == 0  # still nothing on database


def test_cancel_button():

    mocked_app = Mock()
    view = AddTaskView(app=mocked_app)

    # Get the cancel button and simulate a press
    cancel_button = next(
        (
            element for element in view.focusable_elements
            if element.text == "Cancel"
        )
    )
    cancel_button.handler()

    mocked_app.load_list_tasks_view.assert_called_once()
