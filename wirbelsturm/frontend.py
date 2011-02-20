import os
from json import dumps

import bottle
bottle.debug(True)

from bottle import (
    run,
    request,
    response,
    view,
    default_app,
    route,
    redirect,
    TEMPLATE_PATH
    )

from tw.core.middleware import make_middleware
import tw.mods.base

from formencode import Invalid
from formencode.validators import FancyValidator

from tw.api import (
    Widget,
    JSSource,
    JSLink,
    )

from tw.forms import (
    TableForm,
    TextField,
    )

from abl.jquery.core import jquery_js


from .chat import CHAT
from .tornado import start_app



TEMPLATE_PATH.append(os.path.dirname(__file__))



underscore_js = JSLink(modname=__name__,
                       filename="underscore.js"
                       )

backbone_js = JSLink(modname=__name__,
                     filename="backbone.js",
                     javascript=[jquery_js, underscore_js],
                     )


class NotRegistered(FancyValidator):

    def __init__(self, *args, **kwargs):
        kwargs["not_empty"] = True
        super(NotRegistered, self).__init__(*args, **kwargs)
        

    def validate_python(self, username, state):
        if CHAT.has_user(username):
            raise Invalid("User with that name already exists!", username, state)
        

signup_form = TableForm(
    "signup_form",
    fields=[TextField("name", validator=NotRegistered())],
    action="/register"
    )



user_list_js = JSLink(modname=__name__,
                      filename="userlist.js",
                      javascript=[backbone_js]
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
        

        
user_list = UserList("user_list")


@bottle.route('/')
@view("index")
def index():
    return dict(signup_form=signup_form.render(),
                user_list=user_list.render(CHAT.userinfo()))



@bottle.route('/register', method="POST")
def register():
    try:
        value = signup_form.validate(request.POST)
    except Invalid:
        return index()

    userinfo = CHAT.register_user(value["name"])
    redirect("/chat/%s" % userinfo.cookie)



@bottle.route('/chat/:usercookie')
@view("chat")
def chat(usercookie):
    js = JSSource("""
    $(document).ready(function() {
    });
    """ % dict(cookie=usercookie), javascript=[jquery_js]).inject()
    return dict(user_list=user_list.render(CHAT.userinfo()))


test_widget = Widget(
    "test_widget",
    javascript=[JSLink(modname=__name__,
                       filename="test.js",
                       javascript=[jquery_js])],
    template = "<div id='$id'/>"
    )
    

@bottle.route("/ajax_test")
@view("ajax_test")
def ajax_test():
    return dict(test_widget=test_widget.render())


count = 0

@route('/ajax_call')
def ajax_call():
    global count
    count += 1
    if not count % 10:
        raise Exception()
    return {'test' : count}

def make_app():
    app = make_middleware(default_app(), {
        'toscawidgets.middleware.inject_resources': True,
        },
                          stack_registry=True,
                          )
    return app


def app_factory(global_config, tornado_port=8888, **local_conf):
    tornado_port = int(tornado_port)
    start_app(tornado_port)
    app = make_app()
    return app

