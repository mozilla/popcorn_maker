Popcorn Gallery
===============

Django app to power the Popcorn Maker! http://mozillapopcorn.org/

The Project structure is based on Mozilla Playdoh http://playdoh.readthedocs.org/en/latest/index.html


Set up the development server
=============================

The setup is recomended to be done in a virtual machine, and this is where vagrant comes in handy.

With vagrant you will have your code in your living in your local filesystem but the application running in a virtual linux machine. You can install the latest Vagrant package from http://vagrantup.com/

Once you have installed vagrant grab a copy of this repository and copy the local vagrant settings from ``vagrantconfig_local.yaml-dist`` to ``vagrantconfig_local.yaml``  and edit as necessary

Please note that this file shouldn't be commited into the repository.

To provision the machine run, this may take a few minutes:

    vagrant up

SSH into the virtual machine:

    vagrant ssh

Install the development dependencies:

    pip install -r requirements/dev.txt
    git submodule update --init --recursive

Edit ``settings/local.py`` with your details


Add to /etc/hosts in your local machine:

    33.33.33.11 local.mozillapopcorn.org

The application should be available at:

    http://localhost.mozillapopcorn.org


Run the test suite
=================

    fab test