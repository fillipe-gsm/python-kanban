import pytest
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys

from python_kanban.models import Todo
from python_kanban.status_container_view import StatusContainer


@pytest.fixture
def todo_entries():
    """A list of three Todo entries with the same status"""
    return [
        Todo.create(title="Task 1"),
        Todo.create(title="Task 2"),
        Todo.create(title="Task 3"),
    ]


def test_status_container_display_content(todo_entries):
    """The todo titles must be in the content"""
    status_container = StatusContainer(todo_entries)

    for todo in todo_entries:
        assert any(
            todo.title in item
            for item in status_container.container.content.text()()
        )


def test_status_container_navigation_key_bindings(todo_entries):
    """By pressing navigation keys the selected line should change"""

    container = StatusContainer(todo_entries)
    processor = KeyProcessor(container.container.get_key_bindings())

    # Pressing `j` or `down` should increase the selected line number
    assert container.selected_line == 0

    processor.feed(KeyPress("j"))
    processor.process_keys()
    assert container.selected_line == 1

    processor.feed(KeyPress(Keys.Down))
    processor.process_keys()
    assert container.selected_line == 2

    # Pressing `k` or `up` should decrease the selected line number
    processor.feed(KeyPress("k"))
    processor.process_keys()
    assert container.selected_line == 1

    processor.feed(KeyPress(Keys.Up))
    processor.process_keys()
    assert container.selected_line == 0


def test_status_container_promotes_todo(todo_entries):

    container = StatusContainer(todo_entries)
    processor = KeyProcessor(container.container.get_key_bindings())

    processor.feed(KeyPress("p"))
    processor.process_keys()

    # Updates only the entry in the `selected_line`
    assert container.entries[0].status == Todo.CHOICES[1][0]
    assert container.entries[1].status == Todo.CHOICES[0][0]
    assert container.entries[2].status == Todo.CHOICES[0][0]


def test_status_container_regress_todo(todo_entries):

    container = StatusContainer(todo_entries)
    processor = KeyProcessor(container.container.get_key_bindings())

    # Promote twice the first entry
    processor.feed(KeyPress("p"))
    processor.feed(KeyPress("p"))
    processor.process_keys()
    assert container.entries[0].status == Todo.CHOICES[2][0]

    # Now regress it once
    processor.feed(KeyPress("r"))
    processor.process_keys()

    # The update should occur only in the `selected_line`
    assert container.entries[0].status == Todo.CHOICES[1][0]
    assert container.entries[1].status == Todo.CHOICES[0][0]
    assert container.entries[2].status == Todo.CHOICES[0][0]
