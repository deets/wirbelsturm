from json import dumps
from tw.api import (
    JSLink,
    Widget,
    )

from abl.jquery.core import jquery_js



underscore_js = JSLink(modname="wirbelsturm",
                       filename="javascript/underscore.js"
                       )

backbone_js = JSLink(modname="wirbelsturm",
                     filename="javascript/backbone.js",
                     javascript=[jquery_js, underscore_js],
                     )

user_list_js = JSLink(modname="wirbelsturm",
                      filename="javascript/userlist.js",
                      javascript=[backbone_js]
                      )
                      

centralstation_js = JSLink(modname="wirbelsturm",
                           filename="javascript/centralstation.js",
                           javascript=[backbone_js],
                           )


class UserList(Widget):

    template = "wirbelsturm.user_list"
    engine_name = "genshi"

    css_class = "user_list"

    javascript = [user_list_js]


    def update_params(self, d):
        super(UserList, self).update_params(d)
        user_list = dumps(d.value)
        self.add_call("""
        $(function() {
          userlist.refresh(%(user_list)s);
        }
        );
        """ % dict(user_list=user_list))
        

        
class CentralStationWidget(Widget):


    params = dict(
        endpoint="""The url where the central-station connects to.""",
        start="""If True (default), start the the dispatch immediatly."""
        )


    endpoint = None
    start = True

    javascript = [centralstation_js]
    
    def update_params(self, d):
        super(CentralStationWidget, self).update_params(d)
        opts = dict(
            endpoint=d.endpoint,
            )
        start = "true" if d.start else "false"
        self.add_call("""
           $(function() {
             // one global
             window.central_station = new CentralStation(%(opts)s);
             if(%(start)s) {
               window.central_station.start();
             }
           });
        """ % dict(opts=dumps(opts),
                   start=start))
