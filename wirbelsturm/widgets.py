from json import dumps
from tw.api import (
    JSLink,
    CSSLink,
    JSSource,
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


centralstation_js = JSLink(modname="wirbelsturm",
                           filename="javascript/centralstation.js",
                           javascript=[backbone_js],
                           )



def central_station(endpoint, start=True):

    opts = dict(
        endpoint=endpoint,
        )
    start = "true" if start else "false"

    return JSSource("""
    $(function() {
      // one global
      window.central_station = new CentralStation(%(opts)s);
      if(%(start)s) {
        window.central_station.start();
      }
    });
    """ % dict(opts=dumps(opts), start=start),
                    javascript = [centralstation_js]
                    )


my_central_station = central_station("/dispatch")


reset_css = CSSLink(modname=__name__,
                   filename="css/reset-min.css"
                   )

user_list_css = CSSLink(modname=__name__,
                       filename="css/user_list.css",
                       css=[reset_css]
                       )


user_list_js = JSLink(modname=__name__,
                      filename="javascript/user_list.js",
                      javascript=[backbone_js, my_central_station]
                      )


class UserList(Widget):

    template = "wirbelsturm.user_list"
    engine_name = "genshi"
    css_class = "user_list"

    css = [user_list_css]
    javascript = [user_list_js]


    def update_params(self, d):
        super(UserList, self).update_params(d)
        user_list = dumps(d.value)
        self.add_call("""
        $(function() {
          UserList.setup_user_list("#%(id)s");
        });
        """ % dict(id=d.id))
        

        
class TestWidget(Widget):


    template = """<div xmlns:py='http://genshi.edgewall.org/' id='${id}' style='width:100px; height:20px; background-color:red;'/>"""

    engine_name = "genshi"

    javascript = [my_central_station]
    
    def update_params(self, d):
        super(TestWidget, self).update_params(d)

        self.add_call("""
        $(function() {
           $('#%s').click(
              function() {
                $.getJSON('/trigger');
              }
           );
        })
        """ % d.id)
