from __future__ import absolute_import
import os
from json import dumps

import bottle
bottle.debug(True)

import logging

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

from tw.api import (
    JSSource,
    )


from abl.jquery.core import jquery_js


from .chat import CHAT
from .tornado import start_app, CentralStation
from .widgets import (
    SignupForm,
    UserList,
    TestWidget,
    MessageEntry,
    MessageList,
    )


TEMPLATE_PATH.append(os.path.dirname(__file__))


logger = logging.getLogger(__name__)


signup_form = SignupForm("signup_form", action="/register")


user_list = UserList("user_list")
message_entry = MessageEntry("message_entry")
message_list = MessageList("message_list")


@bottle.route('/')
@view("index")
def index():
    return dict(signup_form=signup_form.render(),
                user_list=user_list.render(CHAT.userinfos()))


@bottle.route('/register', method="POST")
def register():
    try:
        value = signup_form.validate(dict(request.POST.iteritems()))
    except Invalid:
        return index()

    userinfo = CHAT.register_user(value["name"])
    redirect("/chat/" + userinfo.cookie)


@bottle.route('/chat/:usercookie')
@view("chat")
def chat(usercookie):
    try:
        ui = CHAT[usercookie]
    except KeyError:
        redirect("/")
    return dict(
        user_list=user_list.render(CHAT.userinfos()),
        message_list=message_list.render(),
        message_entry=message_entry.render(usercookie=usercookie),
        )


typing = True
@bottle.route('/trigger')
def trigger():
    global typing
    CHAT.users.values()[0].typing(typing)
    typing = not typing
    return "Triggered"


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

