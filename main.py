import peewee as pw
from dynaconf import settings


db = pw.SqliteDatabase(settings.DB_FILE or "kanban.db")


if __name__ == "__main__":
    from python_kanban.models import Todo
    from python_kanban.app import KanbanApplication

    db.create_tables([Todo])
    application = KanbanApplication()
    application.run()
