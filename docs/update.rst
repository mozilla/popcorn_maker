====================
Update Popcorn Maker
====================


Update application codebase
---------------------------

The application is under heavy development, and when you update there could be a few database or asset changes.

There is an script is provided to make sure it is keep in sync

SSH into the VM::

    vagrant ssh

Run the update script::

    fab update


This will syncronize the database, run any database schema or data migrations, and compile the assets from ``Butter``.


Update the development machine stack
------------------------------------

Sometimes the vagrant stack can get an update as well. If that is the case running::

    vagrant provision
