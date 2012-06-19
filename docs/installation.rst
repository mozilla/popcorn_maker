============
Installation
============


Getting the source code
=======================

Clone the repository and its dependencies::

    git clone --recursive git://github.com/mozilla/popcorn_maker.git

This will take a few minutes.

Setup the application
=====================

The recommended setup is using vagrant and virtual box, you can get them from:

- `Virtualbox <https://www.virtualbox.org/wiki/Downloads>`_
- `Vagrant <http://vagrantup.com/>`_

This will keep the code living in your filesystem but the application running inside a VM.

Once you've installed vagrant, from the root of the repository copy the local vagrant settings::

    cp vagrantconfig_local.yaml-dist vagrantconfig_local.yaml

Edit ``vagrantconfig_local.yaml`` if you want to change any of the defaults.

If you are on an NFS capable OS I recommend that you change ``nfs`` to ``true``.

VirtualBox has know issues sharing files natively, more about this issue: http://vagrantup.com/docs/nfs.html

Now we are ready to provision the machine run::

    vagrant up

This will take a few minutes, so go on and reward yourself with a nice cup of tea!


Update the local settings file
==============================

From the root of the repository copy the local python settings::

    cp popcorn_gallery/settings/local.py-dist popcorn_gallery/settings/local.py

Amend ``popcorn_gallery/settings/local.py``  adding your details:

- ``ADMINS``: Add an email address and a name.
- ``SECRET_KEY``: This can be anything.
- ``HMAC_KEYS``: Uncomment or add your own key inside it.


Add a host alias
================

This is done so you can access the application via: http://local.mozillapopcorn.org and perform the browserid assertion.

If you are on OSX or *NIX add an alias for the site by running the following command in your local machine::

    echo "33.33.33.11 local.mozillapopcorn.org" | sudo tee -a /etc/hosts

Or if you prefer a GUI try http://code.google.com/p/gmask/

Now the application should be available at::

    https://local.mozillapopcorn.org


Runing the test suite
=====================

SSH into the virtualbox::

    vagrant ssh

And run the test suite::

    fab test


Updating the development server
===============================

The development server can be updated from time to time, and it is done via Puppet http://puppetlabs.com/

Update the server by running in your local machine from the root of the project::

    vagrant provision


Puppet Summary
==============

Puppet will provision everything necessary for the development VM to run.

The application stack is composed by:

- MySQL
- Python
- Apache

The web server is ``NGINX`` and proxy-passing whatever is served in the VM from the port ``8000`` to ``80`` and ``443`` and serving most of the static files.

``Nodejs`` is used for compiling the ``Popcorn`` and ``Butter`` assets.


Speed up the server
===================

At the moment the wsgi application is served via apache, which it's a bit hacky in order to pick up the file changes and reload automaticaly.

If you want to speed up the application you could try stop apache and run the application via the development server.

SSH into the virtual box::

    vagrant ssh

Stop apache::

    sudo /etc/init.d/apache2 stop

Run the development server::

    python manage.py runserver


Creating a superuser
====================

From inside the VM run::

    python manage.py createsuperuser
