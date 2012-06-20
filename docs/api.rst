==================
Popcorn Maker API
==================

The Popcorn Maker API is entirely based in the Cornfield API.

All the API points are prefixed with ``/api/`` and the response is JSON.

All the ``POST`` requests must be ``'application/json``

API views are available at ``popcorn_gallery.popcorn.views.api``

All the API endponts are CSRF protected, and require the user to be logged in.


Authentication: Login
---------------------

Authentication is done via `BrowserID <https://browserid.org/>`_ and the endpoint is available at ``/browserid/verify``, this will endpoint will perform the assertion when the browserid mechanics are triggered.

On success the response will return with a ``200`` status code with the following details::

    {
        "status": "okay",
        "email": "USER_EMAIL_ADDRESS"
    }

On failure it will return with a ``200`` status code with the following details::

    {
        "status": "failed"
    }



Authentication Status
---------------------

Determine the authentication status for the current session.

If the user is authenticated, the response will return with a ``200`` status code with the following details::

    {
        "name": "DISPLAY_NAME",
        "username": "USERNAME",
        "email": "EMAIL_ADDRESS",
    }


If the user is *NOT* authenticated the response will have a status code ``403``


List user Projects
------------------

List projects saved that belong to the authed user.

Available at ``/api/projects`` and it uses the ``popcorn_gallery.popcorn.views.api.project_list`` view.

Only ``GET`` requests allowed.

The response will return a ``200`` status code with the following content::

    {
        "error": "okay",
        "projects": [{"name": "PROJECT_NAME", "id": "PROJECT_UUID"}]
    }


Add new Project
---------------

Saves the metadata of a user's Project.

Available at ``/api/project`` and uses the ``popcorn_gallery.popcorn.views.api.project_add`` view.

Only ``POST`` requests allowed.

Required data:

* ``name`` - Name of the project to be saved.
* ``data`` - Metadata associated with this project.
* ``template`` - Slug of the template used with to generate this project.


On sucess the response will return with a ``200`` status code with the following content::

       {
        "error": "okay",
        "project": {
            "_id": "PROJECT_UUID",
            "name": "PROJECT_NAME",
            "template": "TEMPLATE_SLUG",
            "data": "PROJECT_METADATA (JSON DUMP)",
            "created": "CREATION_DATE",
            "modified": "LAST_MODIFIED_DATE"
            },
        "url": "PROJECT_URL",
        }

On failure the response will return with a ``200`` status code with the following content::

    {
     "error": "error",
     "form_errors": [
         {"FIELD_NAME": ["ERROR_DESCRIPTION"]}
         ]
    }


Project Detail
==============

Returns and saves an specific ``Project``.

Available at ``/api/project/{{ UUID }}``

On a successful ``GET`` request the response will return with a ``200`` status code with the following content::

    {
     "error": "okay",
     "url": "PROJECT_URL",
     "project": "PROJECT_METADATA (JSON DUMP)"
    }


A ``POST`` request requires the following data:

* ``name`` - Name of the project to be saved.
* ``data`` - Metadata associated with this project.
* ``template`` - Slug of the template used with to generate this project.

On a successfull ``POST`` request the response will return with a ``200`` status code and the following content::

       {
        "error": "okay",
        "project": {
            "_id": "PROJECT_UUID",
            "name": "PROJECT_NAME",
            "template": "TEMPLATE_SLUG",
            "data": "PROJECT_METADATA (JSON DUMP)",
            "created": "CREATION_DATE",
            "modified": "LAST_MODIFIED_DATE"
            },
        "url': "PROJECT_URL"
       }

On an unsuccessful ``POST`` request the response will return with a ``200`` status code and the following content::

    {
     "error": "error",
     "form_errors": [
         {"FIELD_NAME": ["ERROR_DESCRIPTION"]}
         ]
    }



Publish Project
===============

Publish the selected project and makes available in the community gallery.

It is available at ``/api/publish/{{ UUID }}``

On a successful ``POST`` request, the response will return with a ``200`` status code and the follwing content::

    {
     'error': 'okay',
     'url': 'PROJECT_URL'
    }

