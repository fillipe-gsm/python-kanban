from datetime import datetime
from typing import Dict, List

import peewee as pw
from dynaconf import settings


db = pw.SqliteDatabase(
    settings.DB_FILE if "DB_FILE" in settings else "kanban.db"
)


class Category(pw.Model):
    name = pw.CharField(max_length=30)

    class Meta:
        database = db

    def __str__(self):
        return self.name


class Todo(pw.Model):

    CHOICES = ((0, "To do"), (1, "In progress"), (2, "Done"))

    title = pw.CharField(max_length=100)
    body = pw.TextField(null=True)
    status = pw.IntegerField(choices=CHOICES, default=CHOICES[0][0])
    category = pw.ForeignKeyField(Category, backref="todos", null=True)
    created = pw.DateTimeField(default=datetime.now)
    updated = pw.DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def __str__(self):
        return self.title

    def promote(self):
        """Move the status forward. A 'done' status cannot be moved further"""
        last_status = self.CHOICES[-1][0]
        if self.status < last_status:
            self.status += 1
            self.updated = datetime.now()
            self.save()

    def regress(self):
        """Move the status backwards. A 'to do' status cannot be moved back"""
        first_status = self.CHOICES[0][0]
        if self.status > first_status:
            self.status -= 1
            self.updated = datetime.now()
            self.save()

    @classmethod
    def group_todos_per_status(cls) -> Dict[int, List["Todo"]]:
        todos = Todo.select().order_by(Todo.category, Todo.updated.desc())
        todos_dict: Dict[int, List["Todo"]] = {
            status: [] for status, _ in cls.CHOICES
        }
        for todo in todos:
            todos_dict[todo.status].append(todo)
        return todos_dict

    @classmethod
    def create_todo_with_category(cls, category_name: str = "", **kwargs):
        """Receive a category and create a new todo with it.
        If no such category exists, create it first. If empty, do not create
        anything.
        """
        category = (
            Category.get_or_create(name=category_name)[0]
            if category_name
            else None
        )
        Todo.create(category=category, **kwargs)

    @classmethod
    def update_todo_with_category(
        cls, todo: "Todo", category_name: str = "", **kwargs
    ):
        """Same as before, but just updates a todo
        The category follow the same process: if a new only, create it.
        Notice this DOES NOT update the "updated time". This is meant to track
        only the status movements.
        """
        category = (
            Category.get_or_create(name=category_name)[0]
            if category_name
            else None
        )
        Todo.update(category=category, **kwargs).where(
            cls.id == todo.id
        ).execute()
