=============
Python Kanban
=============

A terminal-based interface written in pure Python for a very plain Kanban board.

Installation
============

.. code:: bash

    pip install python-kanban


Usage
=====

The simplest way to execute it is to run 

.. code:: bash

    python_kanban


in the command line. The navigation keys are (or should be) self-explanatory in the
application.

This will create a ``kanban.db`` database file in the current folder. After
quitting and running ``python_kanban`` again the same database will be loaded
and the tasks are persisted.

If you wish to customize the database file or simply manage multiple files, you
can set an environment variable with:

.. code:: bash

    export DYNACONF_DB_FILE=another_database_file.db

and it will either create another ``another_database_file.db`` file or load it
if already existing.

This is still a work in progress, the looks may be rough in the edges, but most of the main functionality is there already.
