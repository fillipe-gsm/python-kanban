import peewee as pw
from dynaconf import settings


db = pw.SqliteDatabase(
    settings.DB_FILE if "DB_FILE" in settings else "kanban.db"
)


def run_app():
    from python_kanban.models import Todo
    from python_kanban.app import KanbanApplication

    db.create_tables([Todo])
    application = KanbanApplication()
    application.run()


if __name__ == "__main__":
    run_app()
