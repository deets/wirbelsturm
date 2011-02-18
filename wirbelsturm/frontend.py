import os
import bottle
bottle.debug(True)

from bottle import (
    run,
    request,
    response,
    view,
    default_app,
    route,
    TEMPLATE_PATH
    )

from tw.core.middleware import make_middleware
import tw.mods.base

from formencode import Invalid
from formencode.validators import FancyValidator

from tw.api import (
    Widget,
    JSSource,
    )

from tw.forms import (
    TableForm,
    TextField,
    )

from abl.jquery.core import jquery_js


from .chat import CHAT

TEMPLATE_PATH.append(os.path.dirname(__file__))



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
    action="/chat"
    )



class UserList(Widget):

    template = "wirbelsturm.user_list"
    engine_name = "genshi"

    css_class = "user_list"


user_list = UserList("user_list")


@bottle.route('/')
@view("index")
def index():
    return dict(signup_form=signup_form.render(),
                user_list=user_list.render(CHAT.userinfo()))



@bottle.route('/chat', method="POST")
@view("chat")
def chat():
    try:
        value = signup_form.validate(request.POST)
    except Invalid:
        return index()

    userinfo = CHAT.register_user(value["name"])

    js = JSSource("""
    $(document).ready(function() {
      alert('%(cookie)s');
    });
    """ % dict(cookie=userinfo.cookie), javascript=[jquery_js]).inject()
    return dict(user_list=user_list.render(CHAT.userinfo()))


def main():
    app = make_middleware(default_app(), {
        'toscawidgets.middleware.inject_resources': True,
        },
                          stack_registry=True,
                          )
    run(app=app)
