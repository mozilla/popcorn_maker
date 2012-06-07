from django.contrib.auth.models import User
from ..models import Template, TemplateCategory, Project, ProjectCategory


def create_user(handle, with_profile=False):
    """Helper to create Users"""
    email = '%s@%s.com' % (handle, handle)
    user = User.objects.create_user(handle, email, handle)
    if with_profile:
        profile = user.get_profile()
        profile.name = handle.title()
        profile.save()
    return user


def create_template(**kwargs):
    defaults = {
        'name': 'basic',
        'slug': 'basic',
        'template_content': '<!DOCTYPE html5>',
        }
    if kwargs:
        defaults.update(kwargs)
    if not 'author' in kwargs:
        defaults['author'] = create_user('mozilla-test')
    return Template.objects.create(**defaults)


def create_project(**kwargs):
    defaults = {
        "name": 'Popcorn Project',
        "metadata": "{\"data\": \"foo\"}",
        "html": "<!DOCTYPE html5>",
        }
    if kwargs:
        defaults.update(kwargs)
    if not 'template' in kwargs:
        defaults['template'] = create_template()
    if not 'author' in kwargs:
        defaults['author'] = defaults['template'].author
    return Project.objects.create(**defaults)


def create_external_project(**kwargs):
    defaults = {
        "name": 'Popcorn Project',
        "url": 'http://mozillapopcorn.org',
        }
    if not 'author' in kwargs:
        defaults['author'] = create_user('bob')
    if kwargs:
        defaults.update(kwargs)
    return Project.objects.create(**defaults)



def create_template_category(**kwargs):
    defaults = {'name': 'Special'}
    if kwargs:
        defaults.update(kwargs)
    return TemplateCategory.objects.create(**defaults)


def create_project_category(**kwargs):
    defaults = {'name': 'Special'}
    if kwargs:
        defaults.update(kwargs)
    return ProjectCategory.objects.create(**defaults)


HTML_EXPORT = """
<html><head><base href="http://local.mozillapopcorn.org/en-US/template/sample-template/">
    <title>Basic template</title>
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type">
    <style>
        #main, .content-div {
          float: left;
        }
        .content-div {
          min-width: 200px;
          min-height: 200px;
          border: 3px solid #000;
          margin: 5px;
        }
        .container-div {
          float: left;
          text-align: center;
          font-family: helvetica;
          font-style: bold;
        }
        #main {
          min-width: 300px;
          min-height: 200px;
        }
        video {
          position: relative;
          top: 30px;
        }
    </style>
<link href="/static/css/butter.ui.css" rel="stylesheet"><script type="text/javascript" src="/static/external/popcorn-js/popcorn.js"></script><script type="text/javascript" src="/static/external/popcorn-js/modules/player/popcorn.player.js"></script><script src="/static/external/popcorn-js/plugins/attribution/popcorn.attribution.js"></script><script src="/static/external/popcorn-js/plugins/code/popcorn.code.js"></script><script src="/static/external/popcorn-js/plugins/flickr/popcorn.flickr.js"></script><script src="/static/external/popcorn-js/plugins/text/popcorn.text.js"></script><script src="/static/external/popcorn-js/plugins/gml/popcorn.gml.js"></script><script src="/static/external/popcorn-js/plugins/googlefeed/popcorn.googlefeed.js"></script><script src="/static/external/popcorn-js/plugins/googlemap/popcorn.googlemap.js"></script><script src="/static/external/popcorn-js/plugins/image/popcorn.image.js"></script><script src="/static/external/popcorn-js/plugins/lastfm/popcorn.lastfm.js"></script><script src="/static/external/popcorn-js/plugins/linkedin/popcorn.linkedin.js"></script><script src="/static/external/popcorn-js/plugins/lowerthird/popcorn.lowerthird.js"></script><script src="/static/external/popcorn-js/plugins/rdio/popcorn.rdio.js"></script><script src="/static/external/popcorn-js/plugins/subtitle/popcorn.subtitle.js"></script><script src="/static/external/popcorn-js/plugins/tagthisperson/popcorn.tagthisperson.js"></script><script src="/static/external/popcorn-js/plugins/tumblr/popcorn.tumblr.js"></script><script src="/static/external/popcorn-js/plugins/twitter/popcorn.twitter.js"></script><script src="/static/external/popcorn-js/plugins/processing/popcorn.processing.js"></script><script src="/static/external/popcorn-js/plugins/webpage/popcorn.webpage.js"></script><script src="/static/external/popcorn-js/plugins/wikipedia/popcorn.wikipedia.js"></script><script src="/static/external/popcorn-js/plugins/wordriver/popcorn.wordriver.js"></script><span></span></head><body class="butter-header-spacing butter-tray-spacing minimized">
    <video src="../external/popcorn-js/test/trailer.ogv" tabindex="0" controls="" id="main"></video>
    <div class="container-div">
        <div class="content-div" id="Area1"></div>
        <p>Area 1</p>
    </div>
    <div class="container-div">
        <div class="content-div" id="Area2"></div>
        <p>Area 2</p>
    </div>
    <div id="target-div"></div>


<input value="6a8fda2d2fcf60e5c27c9a6002920222" name="csrfmiddlewaretoken" id="csrf_token_id" type="hidden"><script type="text/javascript">(function(){
var popcorn = Popcorn.smart( '#main', 'http://local.mozillapopcorn.org/en-US/template/external/popcorn-js/test/trailer.ogv', {"frameAnimation":true} );
popcorn.text({
  "start": 1,
  "end": 2,
  "target": "Area2",
  "text": "Popcorn.js",
  "escape": "",
  "multiline": ""
});
popcorn.text({
  "start": 0,
  "end": 3,
  "target": "Area1",
  "text": "test",
  "escape": "",
  "multiline": ""
});

 return popcorn;
}());</script></body></html>
"""
