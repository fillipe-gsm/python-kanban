from datetime import datetime

import peewee as pw


db = pw.SqliteDatabase("kanban.db")


class Todo(pw.Model):

    CHOICES = ((0, "To do"), (1, "In progress"), (2, "Done"))

    title = pw.CharField(max_length=100)
    body = pw.TextField(null=True)
    status = pw.IntegerField(choices=CHOICES, default=CHOICES[0][0])
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