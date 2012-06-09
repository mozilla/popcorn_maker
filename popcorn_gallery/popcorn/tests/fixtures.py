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

METADATA_EXPORT = {
    "targets": [{
        "id": "Target0",
        "name": "Target0",
        "element": "Area1"
    }, {
        "id": "Target1",
        "name": "Target1",
        "element": "Area2"
    }],
    "media": [{
        "id": "Media0",
        "name": "Media0",
        "url": "http://localhost:8888/external/popcorn-js/test/trailer.ogv",
        "target": "main",
        "duration": 64.541666,
        "tracks": [{
            "name": "Track0",
            "id": "Track0",
            "trackEvents": [{
                "id": "TrackEvent0",
                "type": "text",
                "popcornOptions": {
                    "start": 0,
                    "end": 3,
                    "text": "test",
                    "target": "Area1",
                    "escape": "",
                    "multiline": ""
                },
                "track": "Track0",
                "name": "TrackEvent0"
            }]
        }, {
            "name": "Track1",
            "id": "Track1",
            "trackEvents": []
        }, {
            "name": "Track2",
            "id": "Track2",
            "trackEvents": [{
                "id": "TrackEvent1",
                "type": "text",
                "popcornOptions": {
                    "start": 1,
                    "end": 2,
                    "target": "Area2",
                    "text": "Popcorn.js",
                    "escape": "",
                    "multiline": ""
                },
                "track": "Track2",
                "name": "TrackEvent1"
            }]
        }]
    }]
}

HTML_EXPORT = """
<html><head><base href="http://local.mozillapopcorn.org/en-US/template/sample-template/"><link href="//www.google.com/uds/solutions/dynamicfeed/gfdynamicfeedcontrol.css" rel="stylesheet" type="text/css"><link href="//www.google.com/uds/solutions/dynamicfeed/gfdynamicfeedcontrol.css" rel="stylesheet" type="text/css"><script src="//english.wikipedia.org/w/api.php?action=parse&amp;props=text&amp;redirects&amp;page=Cape_Town&amp;format=json&amp;callback=wikiCallback1339091347081"></script><script src="//english.wikipedia.org/w/api.php?action=parse&amp;props=text&amp;redirects&amp;page=Cape_Town&amp;format=json&amp;callback=wikiCallback1339091346879"></script>
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
<link href="/static/css/butter.ui.css" rel="stylesheet"><script type="text/javascript" src="/static/external/popcorn-js/popcorn.js"></script><script type="text/javascript" src="/static/external/popcorn-js/modules/player/popcorn.player.js"></script><script src="/static/external/popcorn-js/plugins/attribution/popcorn.attribution.js"></script><script src="/static/external/popcorn-js/plugins/code/popcorn.code.js"></script><script src="/static/external/popcorn-js/plugins/flickr/popcorn.flickr.js"></script><script src="/static/external/popcorn-js/plugins/text/popcorn.text.js"></script><script src="/static/external/popcorn-js/plugins/gml/popcorn.gml.js"></script><script src="/static/external/popcorn-js/plugins/googlefeed/popcorn.googlefeed.js"></script><script src="/static/external/popcorn-js/plugins/googlemap/popcorn.googlemap.js"></script><script src="/static/external/popcorn-js/plugins/image/popcorn.image.js"></script><script src="/static/external/popcorn-js/plugins/lastfm/popcorn.lastfm.js"></script><script src="/static/external/popcorn-js/plugins/linkedin/popcorn.linkedin.js"></script><script src="/static/external/popcorn-js/plugins/lowerthird/popcorn.lowerthird.js"></script><script src="/static/external/popcorn-js/plugins/rdio/popcorn.rdio.js"></script><script src="/static/external/popcorn-js/plugins/subtitle/popcorn.subtitle.js"></script><script src="/static/external/popcorn-js/plugins/tagthisperson/popcorn.tagthisperson.js"></script><script src="/static/external/popcorn-js/plugins/tumblr/popcorn.tumblr.js"></script><script src="/static/external/popcorn-js/plugins/twitter/popcorn.twitter.js"></script><script src="/static/external/popcorn-js/plugins/processing/popcorn.processing.js"></script><script src="/static/external/popcorn-js/plugins/webpage/popcorn.webpage.js"></script><script src="/static/external/popcorn-js/plugins/wikipedia/popcorn.wikipedia.js"></script><script src="/static/external/popcorn-js/plugins/wordriver/popcorn.wordriver.js"></script><span></span><script src="http://www.google.com/uds/?file=feeds&amp;v=1&amp;async=2" type="text/javascript"></script><script src="http://platform.linkedin.com/js/nonSecureAnonymousFramework?v=0.0.2000-RC1.19673-1339&amp;"></script><link rel="stylesheet" href="http://www.google.com/uds/api/feeds/1.0/77f89919ef841f93359ce886504e4e3f/default+en.css" type="text/css"><script src="http://www.google.com/uds/api/feeds/1.0/77f89919ef841f93359ce886504e4e3f/default+en.I.js" type="text/javascript"></script><script src="http://maps.gstatic.com/cat_js/intl/en_us/mapfiles/api-3/9/2/%7Bcommon,util,geocoder%7D.js" charset="UTF-8" type="text/javascript"></script><style type="text/css">* html #li_ui_li_gen_1339091347722_0 a#li_ui_li_gen_1339091347722_0-link{height:1% !important;}#li_ui_li_gen_1339091347722_0{position:relative !important;overflow:visible !important;display:block !important;}#li_ui_li_gen_1339091347722_0 a#li_ui_li_gen_1339091347722_0-link{border:0 !important;height:20px !important;text-decoration:none !important;padding:0 !important;margin:0 !important;display:inline-block !important;}#li_ui_li_gen_1339091347722_0 a#li_ui_li_gen_1339091347722_0-link:link, #li_ui_li_gen_1339091347722_0 a#li_ui_li_gen_1339091347722_0-link:visited, #li_ui_li_gen_1339091347722_0 a#li_ui_li_gen_1339091347722_0-link:hover, #li_ui_li_gen_1339091347722_0 a#li_ui_li_gen_1339091347722_0-link:active{border:0 !important;text-decoration:none !important;}#li_ui_li_gen_1339091347722_0 a#li_ui_li_gen_1339091347722_0-link:after{content:"." !important;display:block !important;clear:both !important;visibility:hidden !important;line-height:0 !important;height:0 !important;}#li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-logo{background:url(http://static02.linkedin.com/scds/common/u/img/sprite/sprite_connect_v13.png) 0px -276px no-repeat !important;cursor:pointer !important;border:0 !important;text-indent:-9999em !important;overflow:hidden !important;padding:0 !important;margin:0 !important;position:absolute !important;left:0px !important;top:0px !important;display:block !important;width:20px !important;height:20px !important;float:right !important;}#li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-logo{background-position:-20px -276px !important;}#li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-logo, #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-logo{background-position:-40px -276px !important;}.IN-shadowed #li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-logo{}#li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title{color:#333 !important;cursor:pointer !important;display:block !important;white-space:nowrap !important;float:left !important;margin-left:1px !important;vertical-align:top !important;overflow:hidden !important;text-align:center !important;height:18px !important;padding:0 4px 0 23px !important;border:1px solid #000 !important;border-top-color:#E2E2E2 !important;border-right-color:#BFBFBF !important;border-bottom-color:#B9B9B9 !important;border-left-color:#E2E2E2 !important;border-left:0 !important;text-shadow:#FFFFFF -1px 1px 0 !important;line-height:20px !important;border-radius:0 !important;-moz-border-radius:0 !important;border-top-right-radius:2px !important;border-bottom-right-radius:2px !important;-moz-border-radius-topright:2px !important;-moz-border-radius-bottomright:2px !important;background-color:#ECECEC !important;background-image:-moz-linear-gradient(top, #FEFEFE 0%, #ECECEC 100%) !important;}#li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-title{border:1px solid #000 !important;border-top-color:#ABABAB !important;border-right-color:#9A9A9A !important;border-bottom-color:#787878 !important;border-left-color:#04568B !important;border-left:0 !important;background-color:#EDEDED !important;background-image:-moz-linear-gradient(top, #EDEDED 0%, #DEDEDE 100%) !important;}#li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title, #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title{color:#666 !important;border:1px solid #000 !important;border-top-color:#B6B6B6 !important;border-right-color:#B3B3B3 !important;border-bottom-color:#9D9D9D !important;border-left-color:#49627B !important;border-left:0 !important;background-color:#DEDEDE !important;background-image:-moz-linear-gradient(top, #E3E3E3 0%, #EDEDED 100%) !important;}.IN-shadowed #li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title{}.IN-shadowed #li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-title{}.IN-shadowed #li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title, .IN-shadowed #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title{}#li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title-text, #li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title-text *{color:#333 !important;font-size:11px !important;font-family:Arial, sans-serif !important;font-weight:bold !important;font-style:normal !important;display:inline-block !important;background:transparent none !important;vertical-align:baseline !important;height:18px !important;line-height:20px !important;float:none !important;}#li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title-text strong{font-weight:bold !important;}#li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title-text em{font-style:italic !important;}#li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-title-text, #li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-title-text *{color:#000 !important;}#li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title-text, #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title-text, #li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title-text *, #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title-text *{color:#666 !important;}#li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title #li_ui_li_gen_1339091347722_0-mark{display:inline-block !important;width:0px !important;overflow:hidden !important;}.success #li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title{color:#333 !important;border-top-color:#E2E2E2 !important;border-right-color:#BFBFBF !important;border-bottom-color:#B9B9B9 !important;border-left-color:#E2E2E2 !important;background-color:#ECECEC !important;background-image:-moz-linear-gradient(top, #FEFEFE 0%, #ECECEC 100%) !important;}.success #li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title-text, .success #li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title-text *{color:#333 !important;}.IN-shadowed .success #li_ui_li_gen_1339091347722_0 #li_ui_li_gen_1339091347722_0-title{}.success #li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-title{color:#000 !important;border-top-color:#ABABAB !important;border-right-color:#9A9A9A !important;border-bottom-color:#787878 !important;border-left-color:#04568B !important;background-color:#EDEDED !important;background-image:-moz-linear-gradient(top, #EDEDED 0%, #DEDEDE 100%) !important;}.success #li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-title-text, .success #li_ui_li_gen_1339091347722_0.hovered #li_ui_li_gen_1339091347722_0-title-text *{color:#000 !important;}.success #li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title, .success #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title{color:#666 !important;border-top-color:#B6B6B6 !important;border-right-color:#B3B3B3 !important;border-bottom-color:#9D9D9D !important;border-left-color:#49627B !important;background-color:#DEDEDE !important;background-image:-moz-linear-gradient(top, #E3E3E3 0%, #EDEDED 100%) !important;}.success #li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title-text, .success #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title-text, .success #li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title-text *, .success #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title-text *{color:#666 !important;}.IN-shadowed .success #li_ui_li_gen_1339091347722_0.clicked #li_ui_li_gen_1339091347722_0-title, .IN-shadowed .success #li_ui_li_gen_1339091347722_0.down #li_ui_li_gen_1339091347722_0-title{}#li_ui_li_gen_1339091347733_1-container.IN-right {display:inline-block !important;float:left !important;overflow:visible !important;position:relative !important;height:18px !important;padding-left:2px !important;line-height:1px !important;cursor:pointer !important;}#li_ui_li_gen_1339091347733_1.IN-right {display:block !important;float:left !important;height:18px !important;margin-right:4px !important;padding-right:4px !important;background:url(http://static02.linkedin.com/scds/common/u/img/sprite/sprite_connect_v13.png) right -100px no-repeat !important;}#li_ui_li_gen_1339091347733_1-inner.IN-right {display:block !important;float:left !important;padding-left:8px !important;text-align:center !important;background:url(http://static02.linkedin.com/scds/common/u/img/sprite/sprite_connect_v13.png) 0px -60px no-repeat !important;}#li_ui_li_gen_1339091347733_1-content.IN-right {display:inline !important;font-size:11px !important;color:#04558B !important;font-weight:bold !important;font-family:Arial, sans-serif !important;line-height:18px !important;padding:0 5px 0 5px !important;}#li_ui_li_gen_1339091347733_1-container.IN-hovered #li_ui_li_gen_1339091347733_1.IN-right, #li_ui_li_gen_1339091347733_1-container.IN-clicked #li_ui_li_gen_1339091347733_1.IN-right, #li_ui_li_gen_1339091347733_1-container.IN-down #li_ui_li_gen_1339091347733_1.IN-right {background-position-y:-120px !important;}#li_ui_li_gen_1339091347733_1-container.IN-hovered #li_ui_li_gen_1339091347733_1-inner.IN-right, #li_ui_li_gen_1339091347733_1-container.IN-clicked #li_ui_li_gen_1339091347733_1-inner.IN-right, #li_ui_li_gen_1339091347733_1-container.IN-down #li_ui_li_gen_1339091347733_1-inner.IN-right {background-position-y:-80px !important;}#li_ui_li_gen_1339091347733_1-container.IN-empty {display:none !important;}#li_ui_li_gen_1339091347733_1-container.IN-hidden #li_ui_li_gen_1339091347733_1 {display:none !important;}</style><script src="http://maps.gstatic.com/cat_js/intl/en_us/mapfiles/api-3/9/2/%7Bmap%7D.js" charset="UTF-8" type="text/javascript"></script><script src="http://maps.googleapis.com/maps/api/js/AuthenticationService.Authenticate?1shttp%3A%2F%2Flocal.mozillapopcorn.org%2Fen-US%2Ftemplate%2Fsample-template%2F&amp;5e1&amp;callback=_xdc_._cbiiac&amp;token=46947" charset="UTF-8" type="text/javascript"></script><script src="http://maps.googleapis.com/maps/api/js/GeocodeService.Search?4sToronto%2C%20Ontario%2C%20Canada&amp;7sUS&amp;9sen-US&amp;callback=_xdc_._6a1yeh&amp;token=71581" charset="UTF-8" type="text/javascript"></script><script src="http://maps.googleapis.com/maps/api/js/GeocodeService.Search?4sToronto%2C%20Ontario%2C%20Canada&amp;7sUS&amp;9sen-US&amp;callback=_xdc_._6a1yeh&amp;token=71581" charset="UTF-8" type="text/javascript"></script><script src="http://maps.gstatic.com/cat_js/intl/en_us/mapfiles/api-3/9/2/%7Bstats,onion%7D.js" charset="UTF-8" type="text/javascript"></script><style type="text/css">@font-face {
  font-family: "PjsEmptyFont";
  src: url('data:application/x-font-ttf;base64,AAEAAAAKAIAAAwAgT1MvMgAAAAAAAAEoAAAAVmNtYXAAAAAAAAABiAAAACxnbHlmAAAAAAAAAbwAAAAkaGVhZAAAAAAAAACsAAAAOGhoZWEAAAAAAAAA5AAAACRobXR4AAAAAAAAAYAAAAAGbG9jYQAAAAAAAAG0AAAABm1heHAAAAAAAAABCAAAACBuYW1lAAAAAAAAAeAAAAAgcG9zdAAAAAAAAAIAAAAAEAABAAAAAQAAAkgTY18PPPUACwAgAAAAALSRooAAAAAAyld0xgAAAAAAAQABAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEAAAACAAIAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACMAIwAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAMAAQAAAAwABAAgAAAABAAEAAEAAABB//8AAABB////wAABAAAAAAAAAAgAEgAAAAEAAAAAAAAAAAAAAAAxAAABAAAAAAABAAEAAQAAMTcBAQAAAAAAAgAeAAMAAQQJAAEAAAAAAAMAAQQJAAIAAgAAAAAAAQAAAAAAAAAAAAAAAAAA')
       format('truetype');
}</style><style type="text/css">@font-face {
  font-family: "PjsEmptyFont";
  src: url('data:application/x-font-ttf;base64,AAEAAAAKAIAAAwAgT1MvMgAAAAAAAAEoAAAAVmNtYXAAAAAAAAABiAAAACxnbHlmAAAAAAAAAbwAAAAkaGVhZAAAAAAAAACsAAAAOGhoZWEAAAAAAAAA5AAAACRobXR4AAAAAAAAAYAAAAAGbG9jYQAAAAAAAAG0AAAABm1heHAAAAAAAAABCAAAACBuYW1lAAAAAAAAAeAAAAAgcG9zdAAAAAAAAAIAAAAAEAABAAAAAQAAAkgTY18PPPUACwAgAAAAALSRooAAAAAAyld0xgAAAAAAAQABAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEAAAACAAIAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACMAIwAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAMAAQAAAAwABAAgAAAABAAEAAEAAABB//8AAABB////wAABAAAAAAAAAAgAEgAAAAEAAAAAAAAAAAAAAAAxAAABAAAAAAABAAEAAQAAMTcBAQAAAAAAAgAeAAMAAQQJAAEAAAAAAAMAAQQJAAIAAgAAAAAAAQAAAAAAAAAAAAAAAAAA')
       format('truetype');
}</style></head><body class="butter-header-spacing butter-tray-spacing minimized">
    <video src="/static/external/popcorn-js/test/trailer.ogv" tabindex="0" controls="" id="main"></video>
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
var popcorn = Popcorn.smart( '#main', 'http://local.mozillapopcorn.org/static/external/popcorn-js/test/trailer.ogv', {"frameAnimation":true} );
popcorn.text({
  "start": 0,
  "end": 1,
  "text": "test",
  "target": "Area1",
  "escape": "",
  "multiline": ""
});
popcorn.text({
  "start": 1,
  "end": 2,
  "target": "Area2",
  "text": "Popcorn.js",
  "escape": "",
  "multiline": ""
});
popcorn.gml({
  "start": 0,
  "end": 1,
  "gmltag": "29582",
  "target": "Area2"
});
popcorn.linkedin({
  "start": 1,
  "end": 2,
  "type": "share",
  "counter": "right",
  "url": "http://www.google.ca",
  "target": "Area2",
  "apikey": "ZOLRI2rzQS_oaXELpPF0aksxwFFEvoxAFZRLfHjaAhcGPfOX0Ds4snkJpWwKs8gk",
  "memberid": "",
  "format": "",
  "companyid": "",
  "modules": "",
  "productid": "",
  "related": ""
});
popcorn.lastfm({
  "start": 7,
  "end": 8,
  "artist": "yacht",
  "target": "Area2",
  "apikey": "30ac38340e8be75f9268727cb4526b3d"
});
popcorn.image({
  "start": 6,
  "end": 7,
  "src": "https://www.drumbeat.org/media//images/drumbeat-logo-splash.png",
  "target": "Area2",
  "href": "http://mozillapopcorn.org/wp-content/themes/popcorn/images/for_developers.png",
  "text": "Popcorn.js"
});
popcorn.googlemap({
  "start": 5,
  "end": 6,
  "type": "ROADMAP",
  "lat": 43.665429,
  "lng": -79.403323,
  "target": "Area2",
  "zoom": "",
  "location": "Toronto, Ontario, Canada",
  "heading": "",
  "pitch": 1
});
popcorn.googlefeed({
  "start": 4,
  "end": 5,
  "url": "http://zenit.senecac.on.ca/~chris.tyler/planet/rss20.xml",
  "title": "Planet Feed",
  "orientation": "Vertical",
  "target": "Area2"
});
popcorn.flickr({
  "start": 3,
  "end": 4,
  "userid": "35034346917@N01",
  "numberofimages": 10,
  "target": "Area2",
  "tags": "",
  "username": "",
  "apikey": "",
  "height": "50px",
  "width": "50px",
  "padding": "",
  "border": "5px"
});
popcorn.attribution({
  "start": 2,
  "end": 3,
  "nameofwork": "A Shared Culture",
  "copyrightholder": "Jesse Dylan",
  "license": "CC-BY-N6",
  "licenseurl": "http://creativecommons.org/licenses/by-nc/2.0/",
  "target": "Area2",
  "nameofworkurl": "",
  "copyrightholderurl": ""
});
popcorn.wordriver({
  "start": 7,
  "end": 8,
  "text": "hello",
  "color": "red",
  "target": "Area1"
});
popcorn.wikipedia({
  "start": 6,
  "end": 7,
  "title": "Cape Town yo",
  "src": "http://en.wikipedia.org/wiki/Cape_Town",
  "target": "Area1",
  "lang": "english",
  "numberofwords": "200"
});
popcorn.webpage({
  "start": 5,
  "end": 6,
  "id": "webpages-a",
  "src": "http://popcornjs.org/",
  "target": "Area1"
});
popcorn.tagthisperson({
  "start": 3,
  "end": 4,
  "person": "Chuck Norris",
  "image": "http://aviationhumor.net/wp-content/uploads/2011/02/chuck-norris.jpg",
  "target": "Area1",
  "href": ""
});
popcorn.subtitle({
  "start": 2,
  "end": 3,
  "text": "Hello",
  "target": "Media0"
});
popcorn.lowerthird({
  "start": 4,
  "end": 5,
  "salutation": "Mr",
  "name": "Hyde",
  "role": "Monster",
  "target": ""
});
popcorn.text({
  "start": 1,
  "end": 2,
  "text": "Test",
  "target": "Area1",
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
