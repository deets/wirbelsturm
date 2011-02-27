from json import dumps
from hashlib import md5

from abl.util import Bunch

from .centralstation import CentralStation

class UserInfo(object):

    def __init__(self, chat_core, cookie, username):
        self.chat_core = chat_core
        self.cookie = cookie
        self.username = username


    def send_message(self, message):
        self.chat_core.chat(self.username, message)


    def typing(self, typing):
        self.chat_core.typing(self.username, typing)


    def __json__(self):
        return {"id" : self.username, "name" : self.username}


class ChatCore(object):


    def __init__(self):
        self.users = {}
        self.cookie2user = {}


    def has_user(self, username):
        return username in self.users


    def register_user(self, username):
        assert not self.has_user(username)
        cookie = md5(username).hexdigest()
        ui = UserInfo(
            self,
            cookie=cookie,
            username=username,
            )
        self.users[username] = ui
        self.cookie2user[cookie] = username
        CentralStation.instance().post(
            "user_list",
            "add",
            ui.__json__(),
            )
        return ui

    def typing(self, username, typing):
        CentralStation.instance().post(
            "user_list",
            "modify",
            dict(id=username,
                 typing=typing,
                 )
            )
        

    def chat(self, username, message):
        CentralStation.instance().post("message_list",
                                       "add",
                                       dict(username=username, 
                                            message=message))



    def userinfos(self):
        return list(ui.__json__() for ui in sorted(self.users.values(), key=lambda ui: ui.username))


    def __getitem__(self, cookie):
        return self.users[self.cookie2user[cookie]]

        
CHAT = ChatCore()
