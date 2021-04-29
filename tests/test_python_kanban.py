import peewee as pw
import pytest

from python_kanban.models import Todo


test_db = pw.SqliteDatabase(":memory:")
MODELS = (Todo,)


@pytest.fixture(scope="function", autouse=True)
def test_database():
    with test_db.bind_ctx(MODELS) as ctx:
        test_db.create_tables(MODELS)
        yield ctx
        test_db.drop_tables(MODELS)


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

        todo.promote()  # go to next level

        assert old_updated_time == todo.updated


def test_regress_decreases_todo_status():
    todo = Todo.create(title="Thing to do", status=1)
    assert todo.status == todo.CHOICES[1][0]

    todo.regress()

    assert todo.status == todo.CHOICES[0][0]


def test_regress_cannot_go_more_backwards_than_todo():
    """An "to do" todo cannot be regressed back"""
    todo = Todo.create(title="Thing to do")
    assert todo.status == todo.CHOICES[0][0]

    todo.regress()

    assert todo.status == todo.CHOICES[0][0]
