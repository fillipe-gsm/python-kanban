import pytest
from mock import Mock
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys

from python_kanban.views.list_tasks_view import ListTasksView
from python_kanban.models import Todo


@pytest.fixture
def todo_entries():
    return [
        Todo.create(title="Title 1 to do", status=Todo.CHOICES[0][0]),
        Todo.create(title="Title 2 to do", status=Todo.CHOICES[0][0]),
        Todo.create(title="Title 3 doing", status=Todo.CHOICES[1][0]),
        Todo.create(title="Title 4 done", status=Todo.CHOICES[2][0]),
        Todo.create(title="Title 5 done", status=Todo.CHOICES[2][0]),
        Todo.create(title="Title 6 done", status=Todo.CHOICES[2][0]),
    ]


@pytest.fixture
def todo_entries_without_status_0():
    return [
        Todo.create(title="Title 3 doing", status=Todo.CHOICES[1][0]),
        Todo.create(title="Title 4 done", status=Todo.CHOICES[2][0]),
        Todo.create(title="Title 5 done", status=Todo.CHOICES[2][0]),
        Todo.create(title="Title 6 done", status=Todo.CHOICES[2][0]),
    ]


@pytest.fixture
def todo_entries_without_status_1():
    return [
        Todo.create(title="Title 1 to do", status=Todo.CHOICES[0][0]),
        Todo.create(title="Title 2 to do", status=Todo.CHOICES[0][0]),
        Todo.create(title="Title 4 done", status=Todo.CHOICES[2][0]),
        Todo.create(title="Title 5 done", status=Todo.CHOICES[2][0]),
        Todo.create(title="Title 6 done", status=Todo.CHOICES[2][0]),
    ]


def test_list_view_layout(todo_entries):
    """
    Ensure there are two main portions: the main view with the Kanban table,
    and a help text
    """
    view = ListTasksView()
    layout = view.layout

    assert len(layout.container.children) == 2


def test_focus_to_first_container_by_default(todo_entries):
    """Ensure the first status container (Todo) has focus by default"""
    view = ListTasksView()
    view.load_view()

    assert view.focused_element == 0
    assert view.layout.has_focus(view.status_containers[0])


def test_focus_to_second_container_if_no_todo_tasks(
    todo_entries_without_status_0
):
    """
    If there are no tasks in status 'Todo', the focus must be on the second
    container
    """
    view = ListTasksView()

    assert view.focused_element == 1
    assert view.layout.has_focus(view.status_containers[1])


def test_a_should_load_add_task_view(todo_entries):
    mocked_app = Mock()
    view = ListTasksView(app=mocked_app)

    processor = KeyProcessor(view.load_key_bindings())
    processor.feed(KeyPress("a"))
    processor.process_keys()

    mocked_app.load_add_task_view.assert_called_once()


def test_right_moves_to_next_container(todo_entries):
    """
    Pressing "right" or "l" key should give focus to next status container.
    This only goes as farther as the rightmost one.
    """
    view = ListTasksView()

    processor = KeyProcessor(view.load_key_bindings())

    processor.feed(KeyPress("l"))
    processor.process_keys()

    assert view.focused_element == 1
    assert view.layout.has_focus(view.status_containers[1])

    processor.feed(KeyPress(Keys.Right))
    processor.process_keys()

    assert view.focused_element == 2
    assert view.layout.has_focus(view.status_containers[2])

    processor.feed(KeyPress("l"))
    processor.process_keys()

    # Further presses should keep the same last container
    assert view.focused_element == 2
    assert view.layout.has_focus(view.status_containers[2])

    processor.feed(KeyPress(Keys.Right))
    processor.process_keys()

    assert view.focused_element == 2
    assert view.layout.has_focus(view.status_containers[2])


def test_right_skips_empty_container(todo_entries_without_status_1):
    """
    Here, it should skip container 1 (Doing) since there are no todos there.
    """
    view = ListTasksView()

    processor = KeyProcessor(view.load_key_bindings())

    processor.feed(KeyPress("l"))
    processor.process_keys()

    assert view.focused_element == 2
    assert view.layout.has_focus(view.status_containers[2])


def test_left_moves_to_previous_container(todo_entries):
    """
    Pressing "left" or "h" key should give focus to previous status container.
    This only goes as farther as the leftmost one.
    """
    view = ListTasksView()

    # Force focused position in container 2
    view.focused_element = 2

    processor = KeyProcessor(view.load_key_bindings())

    processor.feed(KeyPress("h"))
    processor.process_keys()

    assert view.focused_element == 1
    assert view.layout.has_focus(view.status_containers[1])

    processor.feed(KeyPress(Keys.Left))
    processor.process_keys()

    assert view.focused_element == 0
    assert view.layout.has_focus(view.status_containers[0])

    processor.feed(KeyPress("h"))
    processor.process_keys()

    # Further presses should keep the same first container
    assert view.focused_element == 0
    assert view.layout.has_focus(view.status_containers[0])

    processor.feed(KeyPress(Keys.Left))
    processor.process_keys()

    assert view.focused_element == 0
    assert view.layout.has_focus(view.status_containers[0])


def test_left_skips_empty_container(todo_entries_without_status_1):
    """
    Here, it should skip container 1 (Doing) since there are no todos there.
    """

    view = ListTasksView()

    # Force focused position in container 2
    view.focused_element = 2

    processor = KeyProcessor(view.load_key_bindings())

    processor.feed(KeyPress("h"))
    processor.process_keys()

    assert view.focused_element == 0
    assert view.layout.has_focus(view.status_containers[0])


def test_q_quits_application(todo_entries):
    mocked_app = Mock()
    view = ListTasksView(app=mocked_app)

    processor = KeyProcessor(view.load_key_bindings())
    processor.feed(KeyPress("q"))
    processor.process_keys()

    mocked_app.exit.assert_called_once()


def test_check_focus_if_initial_container_is_provided(todo_entries):
    view = ListTasksView(initial_container_focus=2)

    assert view.focused_element == 2
    assert view.layout.has_focus(view.status_containers[2])
