import peewee as pw
import pytest

from python_kanban.models import Todo


test_db = pw.SqliteDatabase(":memory:")
MODELS = (Todo,)


@pytest.fixture(scope="function", autouse=True)
def test_database():
    """A database created before each test function and destroyed just after"""
    with test_db.bind_ctx(MODELS) as ctx:
        test_db.create_tables(MODELS)
        yield ctx
        test_db.drop_tables(MODELS)
