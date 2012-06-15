=========
Templates
=========

Adding templates
================

Only admins/superusers are allowed to add templates to the gallery.
You must create a superuser as specified in the above step.

Once that has been done, visit::

http://local.mozillapopcorn.org/admin

In your browser and login to the Django Admin interface.

There you can choose to add a template file by file, or import a zip file.
A sample zipped template can be found at https://github.com/alfredo/popcorn_gallery_template

Now you must set each file to the proper type:

- config
- default track events
- static assets
- template html

Once that has all ben set, click the publish checkbox at the bottom of the page, then save your changes.


Template Sanitation
===================

There are two points where the user generated content is added to the PM site, the templates and the projects

At the moment the templates are only added by trusted users, so the rules to do this are fairly relaxed, they are procesed to make sure the media paths are correct and that things fall into place once they are saved in the server.

The HTML and JSON stream served to the templates are preprocessed on save and the sanitation mechanics work pipe-like so there is room sanitize further this content in the future when this is open to more users.

The templates are imported in bulk and filters the bundled files imported by extension, they are saved using a Template specific storage in order to isolate the user generated content.

The butter projects are generated using the templates as a base, and they are populated using user specific metadata.

The metadata saved is sanitized using bleach for any string content. This as well as a pipe like we can add extra validation If we want to.

The final html export of the project is generated using the template and the saved metadata in the server side.
