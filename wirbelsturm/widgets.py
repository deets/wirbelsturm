from __future__ import absolute_import

from json import dumps
from tw.api import (
    JSLink,
    CSSLink,
    JSSource,
    Widget,
    WidgetsList,
    )

from tw.forms import (
    TableForm,
    TextField,
    )

from abl.jquery.core import jquery_js

from .validators import NotRegistered



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
    """
    This function creates a JSSource widget which
    should be declared as dependency for all widgets
    that have java-script that relies on the existence
    of a "central_station".
    """
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


super_chat_css = CSSLink(modname=__name__,
                         filename="css/super_chat.css",
                         css=[reset_css]
)



class SignupForm(TableForm):

    css = [CSSLink(modname=__name__,
                         filename="css/signup_form.css",
                         css=[super_chat_css])]

    class fields(WidgetsList):
        name = TextField("name", validator=NotRegistered())

    submit_text = "Join"



user_list_css = CSSLink(modname=__name__,
                       filename="css/user_list.css",
                       css=[super_chat_css]
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
          UserList.setup_user_list("#%(id)s", %(user_list)s);
        });
        """ % dict(id=d.id, 
               user_list=user_list))


message_entry_js = JSLink(modname=__name__,
                      filename="javascript/message_entry.js",
                      javascript=[backbone_js, my_central_station]
                      )

message_entry_css = CSSLink(modname=__name__,
                            filename="css/message_entry.css",
                            css=[super_chat_css],
                            )


class MessageEntry(Widget):

    template = "wirbelsturm.message_entry"

    engine_name = "genshi"

    css_class = "message_entry"

    css = [message_entry_css]
    javascript = [message_entry_js]

    params = dict(
        usercookie="The secret to identify the user",
        endpoint="The chat messages/status enpoint",
        )

    endpoint = "/chat_dispatch"

    def update_params(self, d):
        super(MessageEntry, self).update_params(d)
        self.add_call("""
                      $(function() {
                        var el = $('#%(id)s').get(0);
                        window.message_entry_view = new MessageEntryView({ el : el});
                        window.hub = new ChatHub(window.message_entry_view,
                                                 "%(endpoint)s",
                                                 "%(usercookie)s" 
                                                 );
                      });
                      """ % d)
    


message_list_js = JSLink(modname=__name__,
                      filename="javascript/message_list.js",
                      javascript=[backbone_js, my_central_station]
                      )

message_list_css = CSSLink(modname=__name__,
                            filename="css/message_list.css",
                            css=[super_chat_css],
                            )

class MessageList(Widget):

    template = "wirbelsturm.message_list"

    engine_name = "genshi"

    css_class = "message_list"

    css = [message_list_css]
    javascript = [message_list_js]


    def update_params(self, d):
        super(MessageList, self).update_params(d)
        self.add_call("""
                      $(function() {
                        var el = $('#%(id)s').get(0);
                        window.message_list_view = new MessageListView({ el : el});
                      });
                      """ % d)
    
    
    
class TestWidget(Widget):


    template = """<div xmlns:py='http://genshi.edgewall.org/' id='${id}' style='width:100px; height:20px; background-color:red;'/>"""

    engine_name = "genshi"

    javascript = [my_central_station]
    
    def update_params(self, d):
        super(TestWidget, self).update_params(d)

        self.add_call("""
        $(function() {
                      
        })
        """ % d.id)
