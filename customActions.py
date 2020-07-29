import random
import time
import logging
import logging.handlers
import os
import sys
import requests.exceptions
from vk_api.longpoll import VkEventType

cwd = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    level=logging.WARNING
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    os.path.join(cwd, 'log.txt'),
    maxBytes=102400
)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.info("Запуск...")

def tryAgainIfFailed(func, *args, delay=5, maxRetries=5, **kwargs):
    c = maxRetries
    while True:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException:
            time.sleep(delay)
            continue
        except BaseException:
            if maxRetries == 0:
                logger.warning("После %s попыток %s(%s%s) завершился с ошибкой.", c, func.__name__, args, kwargs)
                raise Warning
            logger.warning("Перезапуск %s(%s%s) через %s секунд...", func.__name__, args, kwargs, delay)
            time.sleep(delay)
            if maxRetries > 0:
                maxRetries -= 1
            continue

class customActions:
    def __init__(self, vk, conn, cursor):
        self.vk = vk
        self.conn = conn
        self.cursor = cursor


    def getPeerName(self, id):
        if id > 2000000000:
            self.cursor.execute("""SELECT * FROM chats_cache WHERE chat_id = ?""", (id,))
            fetch = self.cursor.fetchone()
            if fetch is None:
                try:
                    name = tryAgainIfFailed(
                        self.vk.messages.getChat,
                        delay=0.5,
                        chat_id=id-2000000000
                    )["title"]
                    self.cursor.execute("""INSERT INTO chats_cache (chat_id,chat_name) VALUES (?,?)""", (id, name,))
                    self.conn.commit()
                except Warning:
                    name = "Секретный чат, используйте токен другого приложения"
            else:
                name = fetch[1]
        elif id < 0:
            self.cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
            fetch = self.cursor.fetchone()
            if fetch is None:
                name = tryAgainIfFailed(
                    self.vk.groups.getById,
                    delay=0.5,
                    group_id=-id
                )[0]['name']
                self.cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id, name,))
                self.conn.commit()
            else:
                name = fetch[1]
        else:
            self.cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
            fetch = self.cursor.fetchone()
            if fetch is None:
                name = tryAgainIfFailed(
                    self.vk.users.get,
                    delay=0.5,
                    user_id=id
                )[0]
                name = f"{name['first_name']} {name['last_name']}"
                self.cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id, name,))
                self.conn.commit()
            else:
                name = fetch[1]
        return name

    def act(self, event):
        #Место для своего кода
        #Пример:
        #if event.type == VkEventType.MESSAGE_NEW and event.message.find("echo") != -1:
        #    self.vk.messages.send(peer_id=event.peer_id,message=event.message.strip("echo"),random_id=random.getrandbits(64))
        pass
