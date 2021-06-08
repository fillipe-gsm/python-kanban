from datetime import date

from python_kanban.models import Todo


def test_check_todo_defaults():
    title = "Thing to do"
    todo = Todo.create(title=title)

    assert todo.title == title
    assert not todo.body
    assert todo.status == todo.CHOICES[0][0]


class TestPromote:
    def test_promote_increases_todo_status(self):
        todo = Todo.create(title="Thing to do")
        assert todo.status == todo.CHOICES[0][0]

        todo.promote()

        assert todo.status == todo.CHOICES[1][0]

    def test_promote_goes_no_further_than_done(self):
        """An already done todo cannot be promoted further"""
        todo = Todo.create(title="Thing to do", status=Todo.CHOICES[-1][0])
        assert todo.status == todo.CHOICES[-1][0]

        todo.promote()

        assert todo.status == todo.CHOICES[-1][0]

    def test_promote_updates_updated_time_if_todo_is_promoted(self):
        todo = Todo.create(title="Thing to do")
        old_updated_time = todo.updated

        todo.promote()

        assert old_updated_time < todo.updated

    def test_promote_keeps_updated_time_if_at_last_status(self):
        todo = Todo.create(title="Thing to do", status=Todo.CHOICES[-1][0])
        old_updated_time = todo.updated

        todo.promote()

        assert old_updated_time == todo.updated


class TestRegress:
    def test_regress_decreases_todo_status(self):
        todo = Todo.create(title="Thing to do", status=1)
        assert todo.status == todo.CHOICES[1][0]

        todo.regress()

        assert todo.status == todo.CHOICES[0][0]

    def test_regress_cannot_go_more_backwards_than_todo(self):
        """An "to do" todo cannot be regressed back"""
        todo = Todo.create(title="Thing to do")
        assert todo.status == todo.CHOICES[0][0]

        todo.regress()

        assert todo.status == todo.CHOICES[0][0]

    def test_regress_updates_updated_time_if_todo_is_regressed(self):
        todo = Todo.create(title="Thing to do", status=1)
        old_updated_time = todo.updated

        todo.regress()

        assert old_updated_time < todo.updated

    def test_regress_keeps_updated_time_if_at_first_status(self):
        todo = Todo.create(title="Thing to do")
        old_updated_time = todo.updated

        todo.regress()

        assert old_updated_time == todo.updated


def test_list_todos():
    """"""
    # Create a list of todos with different statuses and updated times
    CHOICES = Todo.CHOICES
    todos = [
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

    expected = {
        CHOICES[0][0]: [todos[1], todos[0]],
        CHOICES[1][0]: [todos[3], todos[2]],
        CHOICES[2][0]: [todos[5], todos[4]],
    }

    todos_dict = Todo.group_todos_per_status()

    assert todos_dict == expected
