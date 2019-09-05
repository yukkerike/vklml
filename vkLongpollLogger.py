import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType   
import sqlite3
import os
import json
import signal
import threading
import time

ACCESS_TOKEN = ""

def interuppt_handler(signum, frame):
        conn.commit()
        cursor.close()
        tableWatcher.cancel()
        os._exit(0)
signal.signal(signal.SIGINT, interuppt_handler)

def bgWatcher():
        cursor.execute("""DELETE FROM messages WHERE timestamp < ?""", (int(time.time())-86400,))
        conn.commit()

def activityReport(message_id, timestamp, isEdited=False, attachments="", message=""):
        peer_name = user_name = oldMessage = oldAttachments = date = fwd = row = ""
        if attachments is None:
                attachments=""
        date = time.ctime(timestamp)
        if not os.path.exists(os.path.join(cwd, "mesAct")):
                os.makedirs(os.path.join(cwd, "mesAct"))
        if not os.path.exists(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y")+".html")):
                f = open(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y")+".html"),'w')
                f.write("""<table cellspacing="0" border="1" width="100%" frame="hsides" white-space="pre-wrap"></table>
                <script>
                function spoiler(elem_id) {
                for (i = 1; i < document.getElementById(elem_id).children.length; i++) {
                        let data = document.getElementById(elem_id).children[i].getAttribute('data-src');
                        if (document.getElementById(elem_id).children[i].hidden == !0) {
                        document.getElementById(elem_id).children[i].removeAttribute("hidden");
                        if (data !== null) document.getElementById(elem_id).children[i].src = document.getElementById(elem_id).children[i].getAttribute('data-src')
                        } else {
                        if (data !== null) document.getElementById(elem_id).children[i].removeAttribute("src");
                        document.getElementById(elem_id).children[i].hidden = !0
                        }
                }
                }
                </script>""")
                f.close()
        messagesActivities = open(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y")+".html"),'r')
        messagesDump = messagesActivities.read()
        messagesActivities.close()
        messagesActivities = open(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y")+".html"),'w')
        cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (message_id,))
        fetch = cursor.fetchone()
        if not fetch[1] is None:
                peer_name = fetch[1]
        user_name = fetch[3]
        if not fetch[5] is None:
                oldMessage = fetch[5]
        if not fetch[6] is None:
                oldAttachments = fetch[6]
        if not fetch[8] is None:
                fwd = fetch[8]
        if peer_name != "":
                row="<tr><td>"+str(message_id)+"</td><td>"+peer_name+"</td><td>"
        
        row="<tr><td>"+str(message_id)+"</td><td><a href='https://vk.com/id"+str(fetch[2])+"'>"+user_name+"</a></td><td>"
        if isEdited:
                if oldMessage != "":
                        row+="<b>Старое </b><br />"+oldMessage+"</td><td>"
                if message != "":
                        row+="<b>Новое </b><br />"+message+"</td><td>"
                if oldAttachments != "":
                        oldAttachments=json.loads(oldAttachments)
                        row+="""<b>Старое <br /></b><div id="{0}_{1}_old" style="display: table;"><button id="{0}_{1}_old" onClick="spoiler(this.id)" style="display: table-cell;">Распахнуть</button>""".format(message_id,timestamp)
                        for i in range(oldAttachments['count']):
                                urlSplit = oldAttachments['urls'][i].split(".")
                                if len(urlSplit[3].split(",")) == 1:
                                        urlSplit = urlSplit[3]
                                        if urlSplit == "jpg":
                                                row+="""<img data-src="{}" hidden></img>""".format(oldAttachments['urls'][i])
                                        if urlSplit == "ogg":
                                                row+="""<audio src="{}" controls hidden></audio>""".format(oldAttachments['urls'][i])
                                elif len(urlSplit[3].split(",")) == 2:
                                        urlSplit = [".".join(urlSplit[:3]),]+urlSplit[3].split(",")
                                        row+="""<a href="{}" hidden>Видео<img src="{}" loading="lazy"></img></a>""".format("../vkGetVideoLink.html?"+urlSplit[2],urlSplit[0]+"."+urlSplit[1])
                                else:
                                        row+="""<a href="{}" hidden>Документ</a>""".format(oldAttachments['urls'][i])
                        row+="</div></td><td>"
                if attachments != "":
                        attachments=json.loads(attachments)
                        row+="""<b>Новое <br /></b><div id="{0}_{1}_new" style="display: table;"><button id="{0}_{1}_new" onClick="spoiler(this.id)" style="display: table-cell;">Распахнуть</button>""".format(message_id,timestamp)
                        for i in range(attachments['count']):
                                urlSplit = attachments['urls'][i].split(".")
                                if len(urlSplit[3].split(",")) == 1:
                                        urlSplit = urlSplit[3]
                                        if urlSplit == "jpg":
                                                row+="""<img data-src="{}" hidden></img>""".format(attachments['urls'][i])
                                        if urlSplit == "ogg":
                                                row+="""<audio src="{}" controls hidden></audio>""".format(oldAttachments['urls'][i])
                                elif len(urlSplit[3].split(",")) == 2:
                                        urlSplit = [".".join(urlSplit[:3]),]+urlSplit[3].split(",")
                                        row+="""<a href="{}" hidden>Видео<img src="{}" loading="lazy"></img></a>""".format("../vkGetVideoLink.html?"+urlSplit[2],urlSplit[0]+"."+urlSplit[1])
                                else:
                                        row+="""<a href="{}" hidden>Документ</a>""".format(attachments['urls'][i])
                        row+="</div></td><td>"
                row+=date+"</td>"
                if fwd != "":
                        row+="<td>"+"<br />".join(fwd.split("\n"))
                row+="</tr>"
        else:
                if oldMessage != "":
                        row+="<b>Удалено <br /></b>"+oldMessage+"</td><td>"
                if oldAttachments != "":
                        oldAttachments=json.loads(oldAttachments)
                        row+="""<b>Удалено <br /></b><div id="{0}_{1}_old" style="display: table;"><button id="{0}_{1}_old" onClick="spoiler(this.id)" style="display: table-cell;">Распахнуть</button>""".format(message_id,timestamp)
                        for i in range(oldAttachments['count']):
                                urlSplit = oldAttachments['urls'][i].split(".")
                                if len(urlSplit[3].split(",")) == 1:
                                        urlSplit = urlSplit[3]
                                        if urlSplit == "jpg":
                                                row+="""<img data-src="{}" hidden></img>""".format(oldAttachments['urls'][i])
                                        if urlSplit == "ogg":
                                                row+="""<audio src="{}" controls hidden></audio>""".format(oldAttachments['urls'][i])
                                elif len(urlSplit[3].split(",")) == 2:
                                        urlSplit = [".".join(urlSplit[:3]),]+urlSplit[3].split(",")
                                        row+="""<a href="{}" hidden>Видео<img src="{}" loading="lazy"></img></a>""".format("../vkGetVideoLink.html?"+urlSplit[2],urlSplit[0]+"."+urlSplit[1])
                                else:
                                        row+="""<a href="{}" hidden>Документ</a>""".format(oldAttachments['urls'][i])
                        row+="</div></td><td>"
                row+=date+"</td>"
                if fwd != "":
                        row+="<td>"+"<br />".join(fwd.split("\n"))
                row+="</tr>"
        messagesDump = messagesDump[:85]+row+messagesDump[85:]
        messagesActivities.write(messagesDump)
        messagesActivities.close()
        if attachments != "":
                attachments = json.dumps(attachments)
        else:
                attachments = None
        cursor.execute("""UPDATE messages SET message = ?, attachments = ? WHERE message_id = ?""", (message, attachments, message_id,))
def getAttachments(message_id):
        attachments = vk_session.method("messages.getById",{"message_ids":event.message_id})['items'][0]
        fwd_messages = None
        try:
                if attachments['fwd_messages'] == []:
                        fwd_messages = json.dumps(attachments['reply_message'],indent=2,ensure_ascii=False,)
                else:
                        fwd_messages = json.dumps(attachments['fwd_messages'],indent=2,ensure_ascii=False,)
        except(KeyError):
                pass
        attachments = attachments['attachments']
        count = len(attachments)
        urls = {'count': count, 'urls':[]}
        for i in range(count):
                type = attachments[i]['type']
                if type == 'photo':
                        urls['urls'].append(attachments[i][type]['sizes'][len(attachments[i][type]['sizes'])-1]['url'])
                elif type == 'sticker':
                        return "sticker"
                elif type == 'video':
                        urls['urls'].append(attachments[i][type]['photo_320']+","+str(attachments[i][type]['owner_id'])+"_"+str(attachments[i][type]['id'])+"_"+str(attachments[i][type]['access_key']))
                elif type == 'audio_message':
                        urls['urls'].append(attachments[i][type]['link_ogg'])
                elif type == 'fwd':
                        pass
                else:
                        urls['urls'].append(attachments[i][type]['url'])
        if urls['count'] == 0:
                urls = None
        else:
                urls = json.dumps(urls,indent=2,ensure_ascii=False,)
        return urls,fwd_messages

vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session, wait=60, mode=2, preload_messages=True)

cwd = os.getcwd()

if os.path.exists(os.path.join(cwd, "messages.db-journal")):
        os.remove(os.path.join(cwd, "messages.db-journal"))

if not os.path.exists(os.path.join(cwd, "messages.db")):
        conn = sqlite3.connect(os.path.join(cwd, "messages.db"),check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE "messages" (
                "peer_id"	INTEGER,
                "peer_name"	TEXT,
                "user_id"	INTEGER NOT NULL,
                "user_name"	TEXT NOT NULL,
                "message_id"	INTEGER NOT NULL UNIQUE,
                "message"	TEXT,
                "attachments"	TEXT,
                "timestamp"	INTEGER NOT NULL,
                "fwd_messages"  TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE "chats_cache" (
                "chat_id"	INTEGER NOT NULL UNIQUE,
                "chat_name"	TEXT NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE "users_cache" (
                "user_id"	INTEGER NOT NULL UNIQUE,
                "user_name"	TEXT NOT NULL
        )
        """)
        conn.commit()
else:
        conn = sqlite3.connect(os.path.join(cwd, "messages.db"),check_same_thread=False)
        cursor = conn.cursor()

tableWatcher = threading.Thread(target=bgWatcher)
tableWatcher.start()

if not os.path.exists(os.path.join(cwd, "vkGetVideoLink.html")):
        f = open(os.path.join(cwd, 'vkGetVideoLink.html'), 'w')
        f.write("""<!DOCTYPE html>
        <html>
        <body>
        <input id="videos"></input>
        <input type="submit" id="submit" value="Отправить">
        <script>
                let ACCESS_TOKEN = '{}';
                document.getElementById('submit').onclick = function() {{
                document.getElementById('submit').disabled = true;
                var script = document.createElement('SCRIPT');
                script.src = "https://api.vk.com/method/video.get?v=5.101&access_token=" + ACCESS_TOKEN + "&videos=" + videos.value + "&callback=callbackFunc";
                document.getElementsByTagName("head")[0].appendChild(script);
                }}
                function callbackFunc(result) {{
                var frame = document.createElement('iframe');
                frame.src = result.response.items[0]["player"];
                frame.style = "position:absolute;top:0;left:0;width:100%;height:100%;"
                document.getElementsByTagName("div")[0].appendChild(frame);
                }}
                let videos = document.getElementById('videos');
                videos.value = document.location.search.slice(1);
                if (videos.value != "") document.getElementById('submit').click()
        </script>
        <div style="position:relative;padding-top:56.25%;"></div>
        </body>
        </html>""".format(ACCESS_TOKEN))
        f.close()



tableWatcher.join()
tableWatcher = threading.Timer(3600,bgWatcher)
tableWatcher.start()
flags = [262144, 131072, 65536, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
for event in longpoll.listen():
        peer_id = peer_name = user_id = user_name = message_id = message = urls = timestamp = fwd_messages = None    
        try:
                if event.type == VkEventType.MESSAGE_NEW:
                        if event.attachments != {}:
                                urls,fwd_messages = getAttachments(event.message_id)
                                if urls == "sticker":
                                        continue
                        else:
                                urls = None
                        if event.peer_id < 0: #Сообщество (игнор)
                                continue
                        elif event.peer_id != event.user_id: #Беседа
                                cursor.execute("""SELECT * FROM chats_cache WHERE chat_id = ?""", (event.peer_id-2000000000,))
                                fetch = cursor.fetchone()
                                if fetch is None:
                                        name = vk_session.method("messages.getChat",{"chat_id":event.peer_id-2000000000})["title"]
                                        cursor.execute("""INSERT INTO chats_cache (chat_id,chat_name) VALUES (?,?)""", (event.peer_id-2000000000,name,))
                                        conn.commit()
                                        fetch = name
                                else:
                                        fetch = fetch[1]
                                peer_name = fetch

                                cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (event.user_id,))
                                fetch = cursor.fetchone()
                                if fetch is None:
                                        name = vk_session.method("users.get",{"user_id":event.user_id})[0]
                                        name = name['first_name'] + " " + name['last_name']
                                        cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (event.user_id,name,))
                                        conn.commit()
                                        fetch = name
                                else:
                                        fetch = fetch[1]        
                                user_name = fetch
                                peer_id = event.peer_id
                                user_id = event.user_id
                        else: #ЛС
                                cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (event.user_id,))
                                fetch = cursor.fetchone()
                                if fetch is None:
                                        name = vk_session.method("users.get",{"user_id":event.user_id})[0]
                                        name = name['first_name'] + " " + name['last_name']
                                        cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (event.user_id,name,))
                                        conn.commit()
                                        fetch = name
                                else:
                                        fetch = fetch[1]
                                peer_name = None
                                peer_id = None
                                user_name = fetch
                                user_id = event.user_id

                        message_id = event.message_id
                        if event.message != "":
                                message = event.message
                        else:
                                message = None
                        timestamp = event.timestamp
                        cursor.execute("""INSERT INTO messages(peer_id,peer_name,user_id,user_name,message_id,message,attachments,timestamp,fwd_messages) VALUES (?,?,?,?,?,?,?,?,?)""",(peer_id,peer_name,user_id,user_name,message_id,message,urls,timestamp,fwd_messages,))
                        conn.commit()
                elif event.type == VkEventType.MESSAGE_EDIT:
                        cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (event.message_id,))
                        fetch = cursor.fetchone()
                        if fetch is None:
                                continue
                        if event.attachments != {}:
                                attachments,fwd_messages = getAttachments(event.message_id)
                        else:
                                attachments = None
                        activityReport(event.message_id, int(time.time()), True, attachments, event.text)
                elif event.type == VkEventType.MESSAGE_FLAGS_SET:
                        cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (event.message_id,))
                        fetch = cursor.fetchone()
                        if fetch is None:
                                continue
                        mask = event.mask
                        messageFlags = []
                        for i in flags:
                                mask-=i
                                if mask < 0:
                                        mask+=i
                                else:
                                        messageFlags.append(i)
                        if (131072 in messageFlags or 128 in messageFlags):
                                activityReport(event.message_id, int(time.time()))
        except ZeroDivisionError as e:
                f = open(os.path.join(cwd, 'errorLog.txt'), 'a+')
                f.write(str(e)+"\n")
                f.close()