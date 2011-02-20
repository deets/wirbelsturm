from __future__ import absolute_import
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

import tornado.ioloop

from tw.core.middleware import make_middleware
import tw.mods.base

from formencode import Invalid

from tw.api import (
    JSSource,
    )

from tw.forms import (
    TableForm,
    TextField,
    )

from abl.jquery.core import jquery_js


from .chat import CHAT
from .tornado import start_app, MainHandler
from .widgets import (
    UserList,
    CentralStationWidget,
    )

from .validators import NotRegistered


TEMPLATE_PATH.append(os.path.dirname(__file__))

        

signup_form = TableForm(
    "signup_form",
    fields=[TextField("name", validator=NotRegistered())],
    action="/register"
    )


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


test_widget = CentralStationWidget("test_widget",
                                   endpoint="/dispatch")


@bottle.route("/ajax_test")
@view("ajax_test")
def ajax_test():
    return dict(test_widget=test_widget.render())




@bottle.route("/trigger")
def trigger():
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_callback(MainHandler.run_callbacks)
    return "Called"





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

