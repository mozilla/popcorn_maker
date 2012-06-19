======
Butter
======

`Butter <https://github.com/mozilla/butter>`_ is included as a submodule and served as a part of a static assets in ``/static/``




Updating Butter
===============

To update butter there are two steps that must happen.

1. Update the ``Butter`` codebase::

    $ cd /butter
    $ git pull --rebase

2. Compile the asserts and move the compiled assets inside the ``/static/`` director. There is a fabric script provided to do this::

    $ fab compile_butter
