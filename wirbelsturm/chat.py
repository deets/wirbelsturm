from json import dumps
from hashlib import md5

from abl.util import Bunch

class UserInfo(object):

    def __init__(self, chat_core, cookie, username):
        self.chat_core = chat_core
        self.cookie = cookie
        self.username = username

    def send_message(self, message):
        self.chat_core.chat(self.username, message)

    def typing(self, typing):
        pass


    def __json__(self):
        return {"id" : self.username, "name" : self.username}


class ChatCore(object):


    def __init__(self):
        self.users = {}
        self.cookie2user = {}
        self.messages = []
        self.mid = 0
        

    def has_user(self, username):
        return username in self.users


    def register_user(self, username):
        assert not self.has_user(username)
        cookie = md5(username).hexdigest()
        self.users[username] = UserInfo(
            self,
            cookie=cookie,
            username=username,
            )
        self.cookie2user[cookie] = username
        return self.users[username]
    

    def chat(self, username, message):
        self.mid += 1
        self.messages.append((self.mid, username, messages))


    def userinfo(self):
        return list(ui.__json__() for ui in sorted(self.users.values(), key=lambda ui: ui.username))


    def __getitem__(self, cookie):
        return self.users[self.cookie2user[cookie]]

        
CHAT = ChatCore()
