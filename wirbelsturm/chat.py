from hashlib import md5

from abl.util import Bunch

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
        self.users[username] = Bunch(
            cookie=cookie,
            username=username,
            )
        self.cookie2user[cookie] = username
        return self.users[username]
    

    def chat(self, username, message):
        self.mid += 1
        self.messages.append((self.mid, username, messages))


    def userinfo(self):
        return sorted(self.users.values(), key=lambda ui: ui.username)
    
        
CHAT = ChatCore()
