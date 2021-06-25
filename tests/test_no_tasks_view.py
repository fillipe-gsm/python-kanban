from mock import Mock
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor

from python_kanban.views.no_tasks_view import NoTasksView


def test_no_task_view_content():
    view_layout = NoTasksView().layout

    assert NoTasksView.MAIN_TEXT == view_layout.container.content.text()


def test_keybinding_add_task():
    """
    When 'a' is pressed, it should trigger the main app to load the 'add task
    view'. Here, we mock `app` and check it its method is called
    """

    mocked_app = Mock()
    view = NoTasksView(app=mocked_app)

    processor = KeyProcessor(view.load_key_bindings())
    processor.feed(KeyPress("a"))
    processor.process_keys()

    mocked_app.load_add_task_view.assert_called_once()


def test_keybinding_quit():
    """
    When 'q' is pressed, check if the `exit` method was called
    """

    mocked_app = Mock()
    view = NoTasksView(app=mocked_app)

    processor = KeyProcessor(view.load_key_bindings())
    processor.feed(KeyPress("q"))
    processor.process_keys()

    mocked_app.exit.assert_called_once()
