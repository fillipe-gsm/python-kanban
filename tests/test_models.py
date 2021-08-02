from datetime import date

import pytest

from python_kanban.models import Category, Todo


@pytest.fixture
def todos():
    # Create a list of todos with different statuses and updated times
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
def todos_with_categories():
    """A list of todos, two with categories"""
    category = Category.create(name="Category")

    return [
        Todo.create(
            title="Task 1: todo",
            category=category,
            updated=date(2021, 1, 1),
        ),
        Todo.create(
            title="Task 2: todo",
            updated=date(2021, 1, 2),
        ),
        Todo.create(
            title="Task 3: todo",
            category=category,
            updated=date(2021, 1, 3),
        )
    ]


def test_check_todo_defaults():
    title = "Thing to do"
    todo = Todo.create(title=title)

    assert todo.title == title
    assert not todo.body
    assert todo.status == todo.CHOICES[0][0]
    assert not todo.category


def test_check_str():
    title = "Thing to do"
    todo = Todo.create(title=title)

    assert todo.__str__() == title


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


def test_list_todos(todos):
    """"""
    CHOICES = Todo.CHOICES

    expected = {
        CHOICES[0][0]: [todos[1], todos[0]],
        CHOICES[1][0]: [todos[3], todos[2]],
        CHOICES[2][0]: [todos[5], todos[4]],
    }

    todos_dict = Todo.group_todos_per_status()

    assert todos_dict == expected


def test_list_todos_with_category(todos_with_categories):
    """The todos are grouped by category first.
    So even though the second comes before the third, it has the same category
    as the first, so they must come together.
    """
    CHOICES = Todo.CHOICES
    expected = {
        CHOICES[0][0]: [
            todos_with_categories[1],
            todos_with_categories[2],
            todos_with_categories[0],
        ],
        CHOICES[1][0]: [],
        CHOICES[2][0]: [],
    }

    todos_dict = Todo.group_todos_per_status()

    assert todos_dict == expected


def test_category_str():
    name = "Category"
    category = Category.create(name=name)

    assert category.__str__() == name


def test_create_todo_with_category():
    title = "Title"
    body = "Body"
    category_name = "Category"

    Todo.create_todo_with_category(
        category_name=category_name, title=title, body=body
    )

    # Ensure both todo and Category were created
    assert Todo.select().count() == 1
    assert Category.select().count() == 1

    todo = Todo.select()[0]
    assert todo.title == title
    assert todo.body == body
    assert todo.category.name == category_name


def test_create_todo_with_empty_category():
    title = "Title"
    body = "Body"

    Todo.create_todo_with_category(
        category_name="", title=title, body=body
    )

    # Ensure only Todo was created
    assert Todo.select().count() == 1
    assert Category.select().count() == 0

    todo = Todo.select()[0]
    assert todo.title == title
    assert todo.body == body
    assert not todo.category


def test_update_todo_with_category():
    # First create a todo
    title = "Title"
    body = "Body"
    category_name = "Category"

    Todo.create_todo_with_category(
        category_name=category_name, title=title, body=body
    )

    todo = Todo.select()[0]

    # Update it with new data
    new_title = "Title 2"
    new_body = "Body 2"
    new_category_name = "Category 2"
    Todo.update_todo_with_category(
        todo, category_name=new_category_name, title=new_title, body=new_body
    )

    # Ensure no new todo was created, only a new Category
    assert Todo.select().count() == 1
    assert Category.select().count() == 2

    new_todo = Todo.select()[0]
    todo.id == new_todo.id
    assert new_todo.title == new_title
    assert new_todo.body == new_body
    assert new_todo.category.name == new_category_name


def test_update_todo_with_empty_category():
    # First create a todo
    title = "Title"
    body = "Body"
    category_name = "Category"

    Todo.create_todo_with_category(
        category_name=category_name, title=title, body=body
    )

    todo = Todo.select()[0]

    # Update it with new data
    new_title = "Title 2"
    new_body = "Body 2"
    new_category_name = ""
    Todo.update_todo_with_category(
        todo, category_name=new_category_name, title=new_title, body=new_body
    )

    # Ensure nothing new was created
    assert Todo.select().count() == 1
    assert Category.select().count() == 1

    new_todo = Todo.select()[0]
    todo.id == new_todo.id
    assert new_todo.title == new_title
    assert new_todo.body == new_body
    assert not new_todo.category
