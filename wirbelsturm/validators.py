from formencode import Invalid
from formencode.validators import FancyValidator

class NotRegistered(FancyValidator):

    def __init__(self, *args, **kwargs):
        kwargs["not_empty"] = True
        super(NotRegistered, self).__init__(*args, **kwargs)
        

    def validate_python(self, username, state):
        if CHAT.has_user(username):
            raise Invalid("User with that name already exists!", username, state)
