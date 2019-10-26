import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType   
import sqlite3
import os
import json
import signal
import threading
import time
import sys

ACCESS_TOKEN = ""

if len(sys.argv)>1 :
        ACCESS_TOKEN = sys.argv[1]
if ACCESS_TOKEN == "":
        raise Exception("Не задан ACCESS_TOKEN")
cwd = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(cwd, "messages.db")):
        conn = sqlite3.connect(os.path.join(cwd, "messages.db"),check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE "messages" (
        "peer_id"	INTEGER NOT NULL,
        "peer_name"	TEXT NOT NULL,
        "user_id"	INTEGER NOT NULL,
        "user_name"	TEXT NOT NULL,
        "message_id"	INTEGER NOT NULL UNIQUE,
        "message"	TEXT,
        "attachments"	TEXT,
        "timestamp"	INTEGER NOT NULL,
        "fwd_messages"  TEXT
)""")
        cursor.execute("""CREATE TABLE "chats_cache" (
        "chat_id"	INTEGER NOT NULL UNIQUE,
        "chat_name"	TEXT NOT NULL
)""")
        cursor.execute("""CREATE TABLE "users_cache" (
        "user_id"	INTEGER NOT NULL UNIQUE,
        "user_name"	TEXT NOT NULL
)""")
        conn.commit()
else:
        conn = sqlite3.connect(os.path.join(cwd, "messages.db"),check_same_thread=False)
        cursor = conn.cursor()

def bgWatcher():
        cursor.execute("""DELETE FROM messages WHERE timestamp < ?""", (int(time.time())-86400,))
        conn.commit()

def interrupt_handler(signum, frame):
        conn.commit()
        cursor.close()
        tableWatcher.cancel()
        os._exit(0)

tableWatcher = threading.Thread(target=bgWatcher)
tableWatcher.start()
signal.signal(signal.SIGINT, interrupt_handler)

if not os.path.exists(os.path.join(cwd, "vkGetVideoLink.html")):
        f = open(os.path.join(cwd, 'vkGetVideoLink.html'), 'w')
        f.write("""<!DOCTYPE html>
<html>
        <head>
                <meta charset="utf-8">
        </head>
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
                                var link = document.createElement('a');
                                link.href = "https://vk.com/dev/video.get?params[videos]=" + videos.value + "&params[count]=2&params[offset]=-1";
                                link.innerText = videos.value;
                                var frame = document.createElement('iframe');
                                frame.src = result.response.items[0]["player"];
                                frame.style = "position:absolute;top:0;left:0;width:100%;height:100%;";
                                document.getElementsByTagName("div")[0].appendChild(link);
                                document.getElementsByTagName("div")[1].appendChild(frame);
                        }}
                        let videos = document.getElementById('videos');
                        videos.value = document.location.search.slice(1);
                        if (videos.value != "") document.getElementById('submit').click()
                </script>
                <div><p>Если видео не проигрывается, прямую ссылку можно получить через api:</p></div>
                <div style="position:relative;padding-top:56.25%;"></div>
        </body>
</html>""".format(ACCESS_TOKEN))
        f.close()

def main():
        for event in longpoll.listen():
                peer_name = user_name = message = attachments = fwd_messages = None    
                try:
                        if event.type == VkEventType.MESSAGE_NEW:
                                if event.from_user:
                                        if event.from_me:
                                                event.user_id = account_id
                                elif event.from_group:
                                        if event.from_me:
                                                event.user_id = account_id
                                        else:
                                                event.user_id = event.peer_id
                                cursor.execute("""INSERT INTO messages(peer_id,peer_name,user_id,user_name,message_id,message,attachments,timestamp,fwd_messages) VALUES (?,?,?,?,?,?,?,?,?)""",(*parseEvent(event.message_id,event.peer_id,event.user_id,event.message,event.attachments,event.from_chat,event.from_user,event.from_group,event.timestamp),))
                                conn.commit()
                        elif event.type == VkEventType.MESSAGE_EDIT:
                                cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (event.message_id,))
                                fetch = cursor.fetchone()
                                if fetch is None:
                                        if event.from_user:
                                                if event.from_me:
                                                        event.user_id = account_id
                                        elif event.from_group:
                                                if event.from_me:
                                                        event.user_id = account_id
                                                else:
                                                        event.user_id = event.peer_id
                                        event.message='⚠️ '+event.message
                                        cursor.execute("""INSERT INTO messages(peer_id,peer_name,user_id,user_name,message_id,message,attachments,timestamp,fwd_messages) VALUES (?,?,?,?,?,?,?,?,?)""",(*parseEvent(event.message_id,event.peer_id,event.user_id,event.message,event.attachments,event.from_chat,event.from_user,event.from_group,event.timestamp),))
                                        conn.commit()
                                if event.attachments != {}:
                                        attachments,fwd_messages = getAttachments(event.message_id)
                                activityReport(event.message_id, event.timestamp, True, attachments, event.text)
                        elif event.type == VkEventType.MESSAGE_FLAGS_SET:
                                cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (event.message_id,))
                                fetch = cursor.fetchone()
                                if fetch is None:
                                        continue
                                if event.mask != 4096: #На голосовые сообщения, отправленные владельцем токена, устанавливается маска, равная 4096, чего в норме быть не может. Это ошибочно расценивается, как удаление сообщения.
                                        mask = event.mask
                                else:
                                        continue
                                messageFlags = []
                                for i in flags:
                                        mask-=i
                                        if mask < 0:
                                                mask+=i
                                        else:
                                                messageFlags.append(i)
                                if (131072 in messageFlags or 128 in messageFlags):
                                        activityReport(event.message_id, int(time.time()))
                except BaseException as e:
                        f = open(os.path.join(cwd, 'errorLog.txt'), 'a+')
                        f.write(str(e)+" "+str(event.message_id)+" "+str(vars(event))+" "+time.ctime(event.timestamp)+"\n\n")
                        f.close()

def attachmentsParse(urls):
    html="""<div>"""
    for i in urls:
            if i.find("sticker") != -1:
                    html+="""<img src="{}"/>""".format(i)
                    continue
            urlSplit = i.split(".")
            if len(urlSplit) < 4: #Сниппет со стороннего сайта
                    html+="""<a href="{0}" target="_blank">{0}</a>""".format(i)
                    continue
            if len(urlSplit[3].split(",")) == 1:
                    urlSplit = urlSplit[3]
                    if urlSplit == "jpg":
                            html+="""<img src="{}" wigth=/>""".format(i)
                    if urlSplit == "mp3":
                            html+="""<audio src="{}" controls></audio>""".format(i)
            elif len(urlSplit[3].split(",")) == 2:
                    urlSplit = [".".join(urlSplit[:3]),]+urlSplit[3].split(",")
                    html+="""
    <a href="{}" target="_blank">Видео
    <img src="{}"/>
    </a>""".format("../vkGetVideoLink.html?"+urlSplit[2],urlSplit[0]+"."+urlSplit[1])
            else:
                    html+="""<a href="{}" target="_blank">Документ</a>""".format(i)
    html+="</div>"
    return html

def getAttachments(message_id):
        attachments = vk_session.method("messages.getById",{"message_ids":message_id})['items'][0]
        fwd_messages = None
        try:
                if attachments['fwd_messages'] != [] or attachments['reply_message'] != {}:
                        if attachments['fwd_messages'] == []:
                                fwd_messages = json.dumps([attachments['reply_message']],indent=1,ensure_ascii=False,)
                        else:
                                fwd_messages = json.dumps(attachments['fwd_messages'],indent=1,ensure_ascii=False,)
        except(KeyError):
                pass
        attachments = attachments['attachments']
        if attachments == []:
                attachments = None
        else:
                attachments = json.dumps(attachments,indent=1,ensure_ascii=False,)
        return attachments,fwd_messages

def parseUrls(attachments):
        urls = []
        for i in attachments:
                type = i['type']
                if type == 'photo':
                        urls.append(i[type]['sizes'][-1]['url'])
                elif type == 'audio_message':
                        urls.append(i[type]['link_mp3'])
                elif type == 'sticker':
                        urls.append(i[type]['images'][0]['url'])
                elif type == "gift" or type == 'poll':
                        continue
                elif type == 'video':
                        urls.append(i[type]['photo_320']+","+str(i[type]['owner_id'])+"_"+str(i[type]['id'])+"_"+str(i[type]['access_key']))
                elif type == 'wall':
                        urls.append("https://vk.com/wall"+str(i[type]['from_id'])+"_"+str(i[type]['id']))
                else:
                        urls.append(i[type]['url'])
        return urls

def getUserName(id):
        if id > 2000000000:
                cursor.execute("""SELECT * FROM chats_cache WHERE chat_id = ?""", (id,))
                fetch = cursor.fetchone()
                if fetch is None:
                        name = vk_session.method("messages.getChat",{"chat_id":id-2000000000})["title"]
                        cursor.execute("""INSERT INTO chats_cache (chat_id,chat_name) VALUES (?,?)""", (id,name,))
                        conn.commit()
                else:
                        name = fetch[1]
        elif id < 0:
                cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
                fetch = cursor.fetchone()
                if fetch is None:
                        name = vk_session.method("groups.getById",{"group_id":-id})[0]['name']
                        cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id,name,))
                        conn.commit()
                else:
                        name = fetch[1]
        else:
                cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
                fetch = cursor.fetchone()
                if fetch is None:
                        name = vk_session.method("users.get",{"user_id":id})[0]
                        name = name['first_name'] + " " + name['last_name']
                        cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id,name,))
                        conn.commit()
                else:
                        name = fetch[1]
        return name

def parseEvent(message_id,peer_id,user_id,message,attachments,from_chat,from_user,from_group,timestamp):
        if attachments != {}:
                attachments,fwd_messages = getAttachments(message_id)
        else:
                attachments = None
                fwd_messages = None
        if from_chat:
                peer_name = getUserName(peer_id)
                user_name = getUserName(user_id)      
        elif from_user:
                peer_name = getUserName(peer_id)
                user_name = getUserName(user_id)
        elif from_group:
                peer_name = getUserName(peer_id)
                user_name = getUserName(user_id)
        if message == "":
                message = None
        return peer_id,peer_name,user_id,user_name,message_id,message,attachments,timestamp,fwd_messages

def fwdParse(fwd):
        html="""<table border="1" width="100%" frame="hsides" style="margin-left:5px;">"""
        for i in fwd:
                user_name = getUserName(i['from_id'])
                if i['from_id'] < 0:
                        html+="""<tr><td>
<a href='https://vk.com/public{}' target="_blank">{}</a>
</td></tr>""".format(-i['from_id'],user_name)
                else:
                        html+="""<tr><td>
<a href='https://vk.com/id{}' target="_blank">{}</a>
</td></tr>""".format(i['from_id'],user_name)
                html+="<tr><td>"+"<br />".join("&gt;".join("&lt;".join(i['text'].split("<")).split(">")).split("\n"))+"<br />"
                if i['attachments'] != []:
                        html+=attachmentsParse(parseUrls(i['attachments']))
                if 'fwd_messages' in i:
                        html+=fwdParse(i['fwd_messages'])
                if 'reply_message' in i:
                        html+=fwdParse([i['reply_message']])
                html+="</td></tr>"
                html+="<tr><td>{}</td></tr>".format(time.ctime(i['date']))
        html+="</table>"
        return html

def activityReport(message_id, timestamp, isEdited=False, attachments=None, message=""):
        try:
                peer_name = user_name = oldMessage = oldAttachments = date = fwd = ""
                attachmentsJ = attachments
                if not attachments is None:
                        attachments = parseUrls(json.loads(attachments))
                row = """
                        <tr>
                                <td>"""
                if not os.path.exists(os.path.join(cwd, "mesAct")):
                        os.makedirs(os.path.join(cwd, "mesAct"))
                if not os.path.exists(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y",time.localtime())+".html")):
                        f = open(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y",time.localtime())+".html"),'w')
                        f.write("""
<html>
        <head>
                <meta charset="utf-8">
                <style>
                        img, a, audio{
                                display: block;
                        }
                        img{
                                max-width: 300px;
                        }
                </style>
        </head>
        <body>
                <table cellspacing="0" border="1" width="100%" frame="hsides" white-space="pre-wrap">
                </table>
        </body>
</html>""")
                        f.close()
                messagesActivities = open(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y",time.localtime())+".html"),'r')
                messagesDump = messagesActivities.read()
                messagesActivities.close()
                messagesActivities = open(os.path.join(cwd, "mesAct", "messages_"+time.strftime("%d%m%y",time.localtime())+".html"),'w')
                cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (message_id,))
                fetch = cursor.fetchone()
                peer_name = fetch[1]
                user_name = fetch[3]
                if not fetch[5] is None:
                        oldMessage = fetch[5]
                if not fetch[6] is None:
                        oldAttachments = parseUrls(json.loads(fetch[6]))
                elif isEdited and message.find("youtu") != -1:
                        row = None
                        return
                if not fetch[8] is None:
                        fwd = json.loads(fetch[8])
                date = time.ctime(fetch[7])
                row+="""{}</td>
                                <td>""".format(str(message_id))
                if fetch[0] > 2000000000:
                        row+="""
                                        <a href='https://vk.com/im?sel=c{}' target="_blank">{}</a>
                                </td>
                                <td>""".format(str(fetch[0]-2000000000),peer_name)
                elif fetch[0] < 0:
                        row+="""
                                        <a href='https://vk.com/public{}' target="_blank">{}</a>
                                </td>
                                <td>""".format(str(-fetch[0]),peer_name)
                else:
                        row+="""
                                        <a href='https://vk.com/id{}' target="_blank">{}</a>
                                </td>
                                <td>""".format(str(fetch[0]),peer_name)
                if fetch[2] < 0:
                        row+="""
                                        <a href='https://vk.com/public{}' target="_blank">{}</a>
                                </td>""".format(str(-fetch[2]),peer_name)
                else:
                        row+="""
                                        <a href='https://vk.com/id{}' target="_blank">{}</a>
                                </td>""".format(str(fetch[2]),user_name)
                if isEdited:
                        row+="""
                                <td width="50%">
                                        <b>Старое</b><br />
                                        """
                        if oldMessage != "":
                                row+="<br />".join(("&gt;".join("&lt;".join(oldMessage.split("<")).split(">"))).split("\n"))+"<br />"
                        if oldAttachments != "":
                                row+="<b>Вложения</b><br />"+attachmentsParse(oldAttachments)+"<br />"
                        if fwd != "":
                                row+="<b>Пересланное</b><br />"+fwdParse(fwd)
                        row+="""
                                </td>
                                <td width="50%">
                                        <b>Новое</b><br />
                                        """
                        if message != "":
                                row+="<br />".join(("&gt;".join("&lt;".join(message.split("<")).split(">"))).split("\n"))+"<br />"
                        if not attachments is None:
                                row+="<b>Вложения</b><br />"+attachmentsParse(attachments)+"<br />"
                        if fwd != "":
                                row+="<b>Пересланное</b><br />"+fwdParse(fwd)
                        row+="</td><td>"
                        row+=date+"</td>"
                else:
                        row+="""
                                <td width="100%" colspan='2'><b>Удалено</b><br />
                                """
                        if oldMessage != "":
                                row+="<br />".join(("&gt;".join("&lt;".join(oldMessage.split("<")).split(">"))).split("\n"))+"<br />"
                        if oldAttachments != "":
                                row+="<b>Вложения</b><br />"+attachmentsParse(oldAttachments)+"<br />"
                        if fwd != "":
                                row+="<b>Пересланное</b><br />"+fwdParse(fwd)
                        row+="</td>\n<td>"
                        row+=date+"</td>"
        except BaseException as e:
                f = open(os.path.join(cwd, 'errorLog.txt'), 'a+')
                f.write(str(e)+" "+row+" "+time.ctime(timestamp)+"\n\n")
                f.close()
        finally:
                if not row is None:
                        row+="</tr>"
                        messagesDump = messagesDump[:478]+row+messagesDump[478:]
                        if not attachments is None:
                                attachments = json.dumps(attachments)
                messagesActivities.write(messagesDump)
                messagesActivities.close()
                if isEdited:
                        cursor.execute("""UPDATE messages SET message = ?, attachments = ? WHERE message_id = ?""", (message, attachmentsJ, message_id,))
                        conn.commit()

vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session, wait=30, mode=2)

flags = [262144, 131072, 65536, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1]
account_id = vk_session.method("users.get")[0]['id']

tableWatcher.join()
tableWatcher = threading.Timer(3600,bgWatcher)
tableWatcher.start()

main()