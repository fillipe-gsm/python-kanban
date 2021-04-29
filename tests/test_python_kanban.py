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


def test_promote_increases_todo_status():
    todo = Todo.create(title="Thing to do")

    assert todo.status == todo.CHOICES[0][0]

    todo.promote()

    assert todo.status == todo.CHOICES[1][0]


def test_promote_goes_no_further_than_done():
    """An already done todo cannot be promoted further"""
    todo = Todo.create(title="Thing to do", status=2)

    assert todo.status == todo.CHOICES[2][0]

    todo.promote()

    assert todo.status == todo.CHOICES[2][0]
