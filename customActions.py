from vk_api.longpoll import VkEventType   
import random
import time

class customActions:
    def __init__(self,vk,conn,cursor):
        self.vk = vk
        self.conn = conn
        self.cursor = cursor

    def tryAgainIfFailed(self, func, delay=5, *args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except BaseException:
                time.sleep(delay)
                continue

    def getPeerName(self,id):
        if id > 2000000000:
            self.cursor.execute("""SELECT * FROM chats_cache WHERE chat_id = ?""", (id,))
            fetch = self.cursor.fetchone()
            if fetch is None:
                name = self.tryAgainIfFailed(self.vk.messages.getChat,delay=0.5,chat_id=id-2000000000)["title"]
                self.cursor.execute("""INSERT INTO chats_cache (chat_id,chat_name) VALUES (?,?)""", (id,name,))
                self.conn.commit()
            else:
                name = fetch[1]
        elif id < 0:
            self.cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
            fetch = self.cursor.fetchone()
            if fetch is None:
                name = self.tryAgainIfFailed(self.vk.groups.getById,delay=0.5,group_id=-id)[0]['name']
                self.cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id,name,))
                self.conn.commit()
            else:
                name = fetch[1]
        else:
            self.cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
            fetch = self.cursor.fetchone()
            if fetch is None:
                name = self.tryAgainIfFailed(self.vk.users.get,delay=0.5,user_id=id)[0]
                name = name['first_name'] + " " + name['last_name']
                self.cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id,name,))
                self.conn.commit()
            else:
                name = fetch[1]
        return name

    def act(self,event):
        #Место для своего кода
        #Пример:
        #if event.type == VkEventType.MESSAGE_NEW and event.message.find("echo") != -1:
        #    self.vk.messages.send(peer_id=event.peer_id,message=event.message.strip("echo"),random_id=random.getrandbits(64))
        pass


