"""This view is shown when there are no created tasks
It should contain simply a message indicating that there are no tasks and the
user should press "a" to add one.
"""

from typing import Optional


class NoTasksView:
    def __init__(self, app: Optional = None):
        self.app = app

    def get_view(self):
        """Return a widget """
