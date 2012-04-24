Popcorn Gallery
===============

Django app to power the Popcorn Maker! http://mozillapopcorn.org/

The Project structure is based on Mozilla Playdoh http://playdoh.readthedocs.org/en/latest/index.html


Set up the development server
=============================

The setup is recomended to be done in a virtual machine, and this is where vagrant comes in handy.

With vagrant you will have your code in your living in your local filesystem but the application running in a virtual linux machine. You can install the latest Vagrant package from http://vagrantup.com/

Once you have installed vagrant grab a copy of this repository and copy the local vagrant settings from ``vagrantconfig_local.yaml-dist`` to ``vagrantconfig_local.yaml`` . Please note that this file shouldn't be commited into the repository.

To provision the machine run, this may take a few minutes::

vagrant up

TODO: Automatize provisioning of the machine packages with puppet. Once this happens the following section will be redundant.


Installing the packages
=======================

Once the machine has been provisioned you can login with::

vagrant ssh

You will find your local copy of the project living under ``/home/vagrant/popcorn_gallery``

The following packages need to be installed:

Python and compiling dependencies::

sudo aptitude install python-dev build-essential
sudo aptitude install python-setuptools python-imaging


Versioning dependencies::

sudo aptitude install git-core subversion mercurial


Database dependencies::

sudo aptitude install mysql-server
sudo aptitude install libmysqlclient-dev

Create a database and a user for the project.


Create Virtual enviroment::

sudo easy_install virtualenv virtualenvwrapper


Add virtualenvwrapper bindings in ~/.bashrc::

source /usr/local/bin/virtualenvwrapper.sh

Source the ~/.bashrc file to add the bindings, this will create the virtualenv scripts::

source ~/.bashrc


Create virtualenv::

mkvirtualenv popcorn


Activate the virtualenv::

workon popcorn


Install dependencies::

pip install -r requirements/dev.txt
git submodule update --init --recursive


Copy local settings from settings/local.py-dist to settings/local.py and update the database and password settings values accordingly (PWD_ALGORITHM and HMAC_KEYS)

Sync the DB::

python manage.py syncdb


Run the development server::

python manage.py runserver 0.0.0.0:8000

The applciation should be accessible via http://localhost:8000


Run the test suite
=================

fab test