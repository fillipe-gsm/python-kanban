from datetime import date

import peewee as pw
import pytest
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor

from python_kanban.models import Todo
from python_kanban.views import TodoContainer, TodoApplication


test_db = pw.SqliteDatabase(":memory:")
MODELS = (Todo,)


@pytest.fixture(scope="function", autouse=True)
def test_database():
    with test_db.bind_ctx(MODELS) as ctx:
        test_db.create_tables(MODELS)
        yield ctx
        test_db.drop_tables(MODELS)


@pytest.fixture
def todo_entries():
    """A list of three Todo entries with the same status"""
    return [
        Todo.create(title="Task 1"),
        Todo.create(title="Task 2"),
        Todo.create(title="Task 3"),
    ]


@pytest.fixture
def todo_entries2():
    """A list with multiple todos with different statuses"""
    CHOICES = Todo.CHOICES
    return [
        # Todos in status "todo": notice the second is more recent
        Todo.create(
            title="Task 1: todo",
            status=CHOICES[0][0],
            updated=date(2021, 1, 1),
        ),
        Todo.create(
            title="Task 2: todo",
            status=CHOICES[0][0],
            updated=date(2021, 1, 2),
        ),
        # Todos in status "in progress"
        Todo.create(
            title="Task 3: in progress",
            status=CHOICES[1][0],
            updated=date(2021, 2, 1),
        ),
        Todo.create(
            title="Task 4: in progress",
            status=CHOICES[1][0],
            updated=date(2021, 2, 2),
        ),
        # Todos in status "done"
        Todo.create(
            title="Task 5: done",
            status=CHOICES[2][0],
            updated=date(2021, 3, 1),
        ),
        Todo.create(
            title="Task 6: done",
            status=CHOICES[2][0],
            updated=date(2021, 3, 2),
        ),
    ]


@pytest.fixture
def todo_entries3():
    """A list of three Todo entries with the same "done" status"""
    CHOICES = Todo.CHOICES
    return [
        Todo.create(title="Task 1", status=CHOICES[2][0]),
        Todo.create(title="Task 2", status=CHOICES[2][0]),
        Todo.create(title="Task 3", status=CHOICES[2][0]),
    ]


class TestTodoContainer:
    def test_todo_container_display_content(self, todo_entries):
        """The todo titles must be in the content"""
        container = TodoContainer(todo_entries)

        for todo in todo_entries:
            assert any(
                todo.title in item
                for item in container.container.content.text()()
            )

    def test_todo_container_navigation_key_bindings(self, todo_entries):
        """By pressing navigation keys the selected line should change
        """
        # TODO: Find how to add a "down" and "up" key presses here

        container = TodoContainer(todo_entries)
        processor = KeyProcessor(container.container.get_key_bindings())

        # Pressing `j` or `down` should increase the selected line number
        assert container.selected_line == 0

        processor.feed(KeyPress("j"))
        processor.process_keys()
        assert container.selected_line == 1

        processor.feed(KeyPress("j"))
        processor.process_keys()
        assert container.selected_line == 2

        # Pressing `k` or `up` should decrease the selected line number
        processor.feed(KeyPress("k"))
        processor.process_keys()
        assert container.selected_line == 1

        processor.feed(KeyPress("k"))
        processor.process_keys()
        assert container.selected_line == 0

    def test_todo_container_promotes_todo(self, todo_entries):

        container = TodoContainer(todo_entries)
        processor = KeyProcessor(container.container.get_key_bindings())

        processor.feed(KeyPress("p"))
        processor.process_keys()

        # Updates only the entry in the `selected_line`
        assert container.entries[0].status == Todo.CHOICES[1][0]
        assert container.entries[1].status == Todo.CHOICES[0][0]
        assert container.entries[2].status == Todo.CHOICES[0][0]

    def test_todo_container_regress_todo(self, todo_entries):

        container = TodoContainer(todo_entries)
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


class TestTodoApplicationListView:
    def test_list_view_has_proper_num_windows(self, todo_entries2):
        """"""
        app = TodoApplication()

        # There is one window per status type
        assert len(app.windows) == len(Todo.CHOICES)

    def test_focus_is_on_current_window(self, todo_entries2):
        """
        When all windows are non-empty, the focus keeps on the current one
        """
        app = TodoApplication()

        app.current_focus = 0
        app.load_list_view()
        assert app.current_focus == 0

        app.current_focus = 1
        app.load_list_view()
        assert app.current_focus == 1

        app.current_focus = 2
        app.load_list_view()
        assert app.current_focus == 2

    def test_focus_moves_to_first_non_empty_window(self, todo_entries3):
        """
        In this case there are only "done" tasks, so the current focus must be
        in the third window.
        """
        app = TodoApplication()
        assert app.current_focus == 2

    def test_next_moves_focus_to_next_window(self, todo_entries2):
        app = TodoApplication()
        assert app.current_focus == 0  # start at "todo" window

        # Press `l` to move right
        processor = KeyProcessor(app.key_bindings)
        processor.feed(KeyPress("l"))
        processor.process_keys()

        assert app.current_focus == 1

        # Press `l` to move right again
        processor = KeyProcessor(app.key_bindings)
        processor.feed(KeyPress("l"))
        processor.process_keys()

        assert app.current_focus == 2

    def test_next_moves_only_if_next_window_is_not_empty(self, todo_entries):
        """
        There are only tasks in the "todo" status, so we should keep in the
        same window
        """
        app = TodoApplication()
        assert app.current_focus == 0  # start at "todo" window

        # Press `l` to move right
        processor = KeyProcessor(app.key_bindings)
        processor.feed(KeyPress("l"))
        processor.process_keys()

        assert app.current_focus == 0  # keep at "todo" window

    def test_prev_moves_focus_to_previous_window(self, todo_entries2):
        app = TodoApplication()
        app.current_focus = 2  # set focus on "done" window

        # Press `h` to move left
        processor = KeyProcessor(app.key_bindings)
        processor.feed(KeyPress("h"))
        processor.process_keys()

        assert app.current_focus == 1

        # Press `h` to move left again
        processor = KeyProcessor(app.key_bindings)
        processor.feed(KeyPress("h"))
        processor.process_keys()

        assert app.current_focus == 0
