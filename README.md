Popcorn Gallery
===============

Django app to power the Popcorn Maker! http://mozillapopcorn.org/

Documentation available at http://popcorn-maker.readthedocs.org/en/latest/

The Project structure is based on Mozilla Playdoh http://playdoh.readthedocs.org/en/latest/index.html


Getting the source code
=======================

Clone the repository and its dependencies:

    git clone --recursive git@github.com:alfredo/popcorn_gallery.git

This will take a few minutes.

Setup the application
=====================

The recommended setup is using vagrant and virtual box, you can get them from:

- Virtualbox: https://www.virtualbox.org/wiki/Downloads
- Vagrant: http://vagrantup.com/

This will keep the code living in your filesystem but the application running inside a VM.

Once you've installed vagrant, from the root of the repository copy the local vagrant settings.

    cp vagrantconfig_local.yaml-dist vagrantconfig_local.yaml

Edit ``vagrantconfig_local.yaml`` if you want to change any of the defaults.

If you are on an NFS capable OS I recommend that you change ``nfs`` to ``true``.

VirtualBox has know issues sharing files natively, more about this: http://vagrantup.com/docs/nfs.html

Now we are ready to provision the machine run.

    vagrant up

This will take a few minutes, so go on and reward yourself with a nice cup of tea!


Update the local settings file
==============================

From the root of the repository copy the local python settings.

    cp popcorn_gallery/settings/local.py-dist popcorn_gallery/settings/local.py

Amend ``popcorn_gallery/settings/local.py``  adding your details:

- ADMINS: Add an email address and a name.
- SECRET_KEY: This can be anything.
- HMAC_KEYS: Uncomment or add your own key inside it.


Updating the application
========================

The application is under heavy development, and when you update there could be a few database or asset changes.

There is an script is provided to make sure it is keep in sync

SSH into the VM:

    vagrant ssh

Run the update script

    fab update


This will syncronize the database, run any database schema or data migrations, and compile the assets from Butter.


Add a host alias
================

This is done so you can access the application via: http://local.mozillapopcorn.org and perform the browserid assertion.

If you are on OSX or *NIX add an alias for the site by running the following command in your local machine:

    echo "33.33.33.11 local.mozillapopcorn.org" | sudo tee -a /etc/hosts

Or if you prefer a GUI try http://code.google.com/p/gmask/

Now the application should be available at:

    http://local.mozillapopcorn.org


Runing the test suite
=====================

SSH into the virtualbox:

    vagrant ssh

And run the test suite:

    fab test


Updating the development server
===============================

The development server can be updated from time to time, and it is done via Puppet http://puppetlabs.com/

Update the server by running in your local machine from the root of the project:

    vagrant provision


Speed up the server
===================

At the moment the wsgi application is served via apache, which it's a bit hacky in order to pick up the file changes and reload automaticaly.

If you want to speed up the application you could try stop apache and run the application via the development server.

NGINX is proxy-passing the port 8000 to 80 and serving most of the static files.

SSH into the virtual box:

    vagrant ssh

Stop apache:

    sudo /etc/init.d/apache2 stop

Run the development server

    python manage.py runserver


Creating a superuser
====================

From inside the VM run:

    python manage.py createsuperuser

Adding templates
================

Only admins/superusers are allowed to add templates to the gallery.
You must create a superuser as specified in the above step.

Once that has been done, visit: `http://local.mozillapopcorn.org/admin` in your browser and login to the Django Admin interface.
There you can choose to add a template file by file, or import a zip file.
A sample zipped template can be found at [https://github.com/alfredo/popcorn_gallery_template](https://github.com/alfredo/popcorn_gallery_template)

Now you must set each file to the proper type:
* config
* default track events
* static assets
* template html

Once that has all ben set, click the publish checkbox at the bottom of the page, then save your changes.
