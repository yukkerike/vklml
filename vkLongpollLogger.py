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
createIndex = False
maxCacheAge = 86400

if createIndex:
    from updateIndex import indexUpdater
    iu = indexUpdater()

if len(sys.argv)>1 :
    ACCESS_TOKEN = sys.argv[1]
if ACCESS_TOKEN == "":
    raise Exception("Не задан ACCESS_TOKEN")
cwd = os.path.dirname(os.path.abspath(__file__))

def tryAgainIfFailed(func, delay=5, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except BaseException:
            time.sleep(delay)
            continue

vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
longpoll = VkLongPoll(vk_session, wait=10, mode=2)
vk = vk_session.get_api()
account_id = tryAgainIfFailed(vk.users.get,delay=0.5)[0]['id']

if not os.path.exists(os.path.join(cwd, "messages.db")):
    conn = sqlite3.connect(os.path.join(cwd, "messages.db"),check_same_thread=False,timeout=15.0)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE "messages" (
    "peer_id"	INTEGER NOT NULL,
    "user_id"	INTEGER NOT NULL,
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
    account_name = tryAgainIfFailed(vk.users.get,delay=0.5,user_id=account_id)[0]
    account_name = account_name['first_name'] + " " + account_name['last_name']
    cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (account_id,account_name,))
    conn.commit()
else:
    conn = sqlite3.connect(os.path.join(cwd, "messages.db"),check_same_thread=False,timeout=15.0)
    cursor = conn.cursor()

def bgWatcher():
    global maxCacheAge
    global stop
    while True:
        while stop:
            time.sleep(2)
        stop = True
        try:
            showMessagesWithDeletedAttachments()
            if maxCacheAge != -1:
                cursor.execute("""DELETE FROM messages WHERE timestamp < ?""", (time.time()-maxCacheAge,))
                conn.commit()
            else:
                maxCacheAge = 86400
            stop = False
        except BaseException:
            stop = False
        time.sleep(maxCacheAge)

def interrupt_handler(signum, frame):
    conn.commit()
    cursor.close()
    try:
        tableWatcher.cancel()
    except AttributeError:
        pass
    os._exit(0)

signal.signal(signal.SIGINT, interrupt_handler)

if not os.path.exists(os.path.join(cwd, "mesAct")):
    os.makedirs(os.path.join(cwd, "mesAct"))

if not os.path.exists(os.path.join(cwd, "mesAct",  "vkGetVideoLink.html")):
    f = open(os.path.join(cwd, "mesAct",  'vkGetVideoLink.html'), 'w')
    f.write("""<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
    </head>
    <body>
        <input id="videos"></input>
        <input type="submit" id="submit" value="Отправить">
        <div><p>Если видео не проигрывается, прямую ссылку можно получить через api:</p></div>
        <div style="position:relative;padding-top:56.25%;"></div>
        <script>
            let ACCESS_TOKEN = '{}';
            document.getElementById('submit').onclick = function() {{
                var link = document.createElement('a');
                link.href = "https://vk.com/dev/video.get?params[videos]=0_0," + videos.value + "&params[count]=1&params[offset]=1";
                link.innerText = videos.value;
                document.getElementById('submit').disabled = true;
                document.getElementsByTagName("div")[0].appendChild(link);
                var script = document.createElement('SCRIPT');
                script.src = "https://api.vk.com/method/video.get?v=5.101&access_token=" + ACCESS_TOKEN + "&videos=" + videos.value + "&callback=callbackFunc";
                document.getElementsByTagName("head")[0].appendChild(script);
            }}
            function callbackFunc(result) {{
                var frame = document.createElement('iframe');
                frame.src = result.response.items[0]["player"];
                frame.style = "position:absolute;top:0;left:0;width:100%;height:100%;";
                document.getElementsByTagName("div")[1].appendChild(frame);
            }}
            let videos = document.getElementById('videos');
            videos.value = document.location.search.slice(1);
            if (videos.value != "") document.getElementById('submit').click()
        </script>
    </body>
</html>""".format(ACCESS_TOKEN))
    f.close()

def predefinedActions():
    global events
    global stop
    while True:
        if events != []:
            event = events.pop(0)
            while stop:
                time.sleep(2)
            stop = True
            attachments = fwd_messages = None      
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
                    cursor.execute("""INSERT INTO messages(peer_id,user_id,message_id,message,attachments,timestamp,fwd_messages) VALUES (?,?,?,?,?,?,?)""",(*parseEvent(event.message_id,event.peer_id,event.user_id,event.message,event.attachments,event.timestamp),))
                    conn.commit()
                elif event.type == VkEventType.MESSAGE_EDIT:
                    hasUpdateTime = True
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
                        cursor.execute("""INSERT INTO messages(peer_id,user_id,message_id,message,attachments,timestamp,fwd_messages) VALUES (?,?,?,?,?,?,?)""",(*parseEvent(event.message_id,event.peer_id,event.user_id,event.message,event.attachments,event.timestamp),))
                        conn.commit()
                    if event.attachments != {}:
                        hasUpdateTime, attachments, fwd_messages = getAttachments(event.message_id)
                    if hasUpdateTime:
                        activityReport(event.message_id, True, attachments, fwd_messages, event.text, hasUpdateTime)
                    cursor.execute("""UPDATE messages SET message = ?, attachments = ?, fwd_messages = ? WHERE message_id = ?""", (event.message, attachments, fwd_messages, event.message_id,))
                    conn.commit()
                elif event.type == VkEventType.MESSAGE_FLAGS_SET:
                    hasUpdateTime = False
                    cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (event.message_id,))
                    fetch = cursor.fetchone()
                    if fetch is None:
                        stop = False
                        continue
                    if event.mask != 4096: #На голосовые сообщения, отправленные владельцем токена, устанавливается маска, равная 4096, чего в норме быть не может. Это ошибочно расценивается, как удаление сообщения.
                        mask = event.mask
                    else:
                        stop = False
                        continue
                    messageFlags = []
                    for i in flags:
                        mask-=i
                        if mask < 0:
                            mask+=i
                        else:
                            messageFlags.append(i)
                    if (131072 in messageFlags or 128 in messageFlags):
                        activityReport(event.message_id)
                        cursor.execute("""DELETE FROM messages WHERE message_id = ?""", (event.message_id,))
                        conn.commit()
            except BaseException as e:
                f = open(os.path.join(cwd, 'errorLog.txt'), 'a+')
                f.write(str(e)+" "+str(event.message_id)+" "+str(vars(event))+" "+time.ctime(event.timestamp)+"\n\n")
                f.close()
            stop = False
        else:
            time.sleep(1)

def main():
    global events
    for event in longpoll.listen():
        events.append(event)

def showMessagesWithDeletedAttachments():
    cursor.execute("""SELECT * FROM messages WHERE attachments IS NOT NULL""")
    fetch_attachments = [[str(i[2]),json.loads(i[4])] for i in cursor.fetchall()]
    cursor.execute("""SELECT * FROM messages WHERE fwd_messages IS NOT NULL""")
    fetch_fwd = [[str(i[2]),json.loads(i[6])] for i in cursor.fetchall()]
    c=0
    for i in range(len(fetch_attachments)):
        for j in fetch_attachments[i-c][1]:
            if j['type'] == 'photo' or j['type'] == 'video' or j['type'] == 'doc':
                break
        else:
            del fetch_attachments[i-c]
            c+=1
    messages_attachments = []
    messages_fwd = []
    for i in [[j[0] for j in fetch_attachments[i:i + 100]] for i in range(0, len(fetch_attachments), 100)]:
        messages_attachments.extend(vk.messages.getById(message_ids=",".join(i))['items'])
    for i in [[j[0] for j in fetch_fwd[i:i + 100]] for i in range(0, len(fetch_fwd), 100)]:
        messages_fwd.extend(vk.messages.getById(message_ids=",".join(i))['items'])
    c=0
    for i in range(len(fetch_attachments)):
        if compareAttachments(messages_attachments[i-c]['attachments'],fetch_attachments[i-c][1]):
            del fetch_attachments[i-c]
            del messages_attachments[i-c]
            c+=1
    for i in range(len(fetch_attachments)):
        activityReport(fetch_attachments[i][0])
        if messages_attachments[i]['attachments'] == []:
            cursor.execute("""UPDATE messages SET attachments = ? WHERE message_id = ?""", (None, fetch_attachments[i][0],))
        else:
            cursor.execute("""UPDATE messages SET attachments = ? WHERE message_id = ?""", (json.dumps(messages_attachments[i]['attachments']), fetch_attachments[i][0],))
    c=0
    for i in range(len(fetch_fwd)):
        if compareFwd(messages_fwd[i-c],{'fwd_messages':fetch_fwd[i-c][1]}):
            del fetch_fwd[i-c]
            del messages_fwd[i-c]
            c+=1
    for i in range(len(fetch_fwd)):
        activityReport(fetch_fwd[i][0])
        if messages_fwd[i]['fwd_messages'] == []:
            cursor.execute("""UPDATE messages SET fwd_messages = ? WHERE message_id = ?""", (None, fetch_fwd[i][0],))
        else:
            cursor.execute("""UPDATE messages SET fwd_messages = ? WHERE message_id = ?""", (json.dumps(messages_fwd[i]['fwd_messages']), fetch_fwd[i][0],))
    conn.commit()

def compareFwd(new,old):
    if 'reply_message' in new:
        new['fwd_messages']=[new['reply_message']]
    if 'reply_message' in old:
        old['fwd_messages']=[old['reply_message']]
    for i in range(len(old['fwd_messages'])):
        if 'fwd_messages' in old['fwd_messages'][i] and 'fwd_messages' in new['fwd_messages'][i]:
            if not compareFwd(new['fwd_messages'][i],old['fwd_messages'][i]):
                return False
        if not compareAttachments(new['fwd_messages'][i]['attachments'],old['fwd_messages'][i]['attachments']):
            return False
    return True

def compareAttachments(new,old):
    if len(new) < len(old):
        return False
    return True

def attachmentsParse(urls):
    html="""<div>"""
    if urls is None:
        return ""
    for i in urls:
        urlSplit = i.split(",")
        if i.find("sticker") != -1:
            html+="""<img src="{}"/>""".format(i)
        elif i.find("jpg") != -1 and i.find(",") == -1:
            html+="""<img src="{}" wigth=/>""".format(i)
        elif i.find("mp3") != -1:
            html+="""<audio src="{}" controls></audio>""".format(i)
        elif len(urlSplit) == 2 and i.find("https://vk.com/audio") == -1:
            html+="""
    <a href="{}" target="_blank">Видео
    <img src="{}"/>
    </a>""".format("./vkGetVideoLink.html?"+urlSplit[1],urlSplit[0])
        elif i.find("https://vk.com/audio") != -1:
            html+="""<a href="{}" target="_blank">{}</a>""".format(i,i[23:-11].replace("%20"," "))
        elif i.find("@") != -1:
            i = i.split("@")
            html+="""<a href="{}" target="_blank">{}</a>""".format(i[1],i[0])
        else:
            html+="""<a href="{0}" target="_blank">{0}</a>""".format(i)
    html+="</div>"
    return html

def getAttachments(message_id):
    mes = tryAgainIfFailed(vk.messages.getById,delay=0.5,message_ids=message_id)['items'][0]
    hasUpdateTime = 'update_time' in mes
    fwd_messages = None
    if 'reply_message' in mes:
        fwd_messages = json.dumps([mes['reply_message']],ensure_ascii=False,)
    elif mes['fwd_messages'] != []:
        fwd_messages = json.dumps(mes['fwd_messages'],ensure_ascii=False,)
    attachments = mes['attachments']
    del mes
    if attachments == []:
        attachments = None
    else:
        attachments = json.dumps(attachments,ensure_ascii=False,)
    return hasUpdateTime, attachments, fwd_messages

def parseUrls(attachments):
    urls = []
    for i in attachments:
        type = i['type']
        if type == 'photo':
            realSizesIndex = 0
            virtSizesIndex = sizes.index(i['photo']['sizes'][0]['type'])
            for j in range(1,len(i['photo']['sizes'])):
                temp = sizes.index(i['photo']['sizes'][j]['type'])
                if temp > virtSizesIndex:
                    virtSizesIndex = temp
                    realSizesIndex = j
            urls.append(i['photo']['sizes'][realSizesIndex]['url'])
        elif type == 'audio_message':
            urls.append(i['audio_message']['link_mp3'])
        elif type == 'sticker':
            urls.append(i['sticker']['images'][0]['url'])
        elif type == 'gift':
            urls.append(i['gift']['thumb_48'])
        elif type == 'link':
            urls.append("Ссылка: "+i['link']['title']+"@"+i['link']['url'])
        elif type == 'video':
            urls.append(i['video']['photo_320']+","+str(i['video']['owner_id'])+"_"+str(i['video']['id'])+"_"+str(i['video']['access_key']))
        elif type == 'wall':
            urls.append("Пост: "+i['wall']['text'][:25]+"@"+"https://vk.com/wall"+str(i['wall']['from_id'])+"_"+str(i['wall']['id']))
        elif type == 'wall_reply':
            urls.append("Комментарий: "+i['wall_reply']['text'][:25]+"@"+"https://vk.com/wall"+str(i['wall_reply']['owner_id'])+"_"+str(i['wall_reply']['post_id'])+"?reply="+str(i['wall_reply']['id']))
        elif type == 'audio':
            urls.append("https://vk.com/audio?q="+str(i['audio']['artist']).replace(" ", "%20")+"%20-%20"+str(i['audio']['title']).replace(" ", "%20")+"&tab=global")
        elif type == 'market':
            urls.append("https://vk.com/market?w=product"+str(i['market']['owner_id'])+"_"+str(i['market']['id']))
        elif type == 'poll':
            urls.append("Голосование: "+i['poll']['question'][:25]+"@"+"https://vk.com/poll"+str(i['poll']['owner_id'])+"_"+str(i['poll']['id']))
        elif type == 'doc':
            urls.append("Документ: "+i['doc']['title']+"@"+i['doc']['url'])
        else:
            try:
                urls.append(i[type]['url'])
            except KeyError:
                pass
    if urls == []:
        return None
    else:
        return urls

def getPeerName(id):
    if id > 2000000000:
        cursor.execute("""SELECT * FROM chats_cache WHERE chat_id = ?""", (id,))
        fetch = cursor.fetchone()
        if fetch is None:
            name = tryAgainIfFailed(vk.messages.getChat,delay=0.5,chat_id=id-2000000000)["title"]
            cursor.execute("""INSERT INTO chats_cache (chat_id,chat_name) VALUES (?,?)""", (id,name,))
            conn.commit()
        else:
            name = fetch[1]
    elif id < 0:
        cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
        fetch = cursor.fetchone()
        if fetch is None:
            name = tryAgainIfFailed(vk.groups.getById,delay=0.5,group_id=-id)[0]['name']
            cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id,name,))
            conn.commit()
        else:
            name = fetch[1]
    else:
        cursor.execute("""SELECT * FROM users_cache WHERE user_id = ?""", (id,))
        fetch = cursor.fetchone()
        if fetch is None:
            name = tryAgainIfFailed(vk.users.get,delay=0.5,user_id=id)[0]
            name = name['first_name'] + " " + name['last_name']
            cursor.execute("""INSERT INTO users_cache (user_id,user_name) VALUES (?,?)""", (id,name,))
            conn.commit()
        else:
            name = fetch[1]
    return name

def parseEvent(message_id, peer_id, user_id, message, attachments, timestamp):
    if attachments != {}:
        hasUpdateTime, attachments, fwd_messages = getAttachments(message_id)
    else:
        attachments = None
        fwd_messages = None
    if message == "":
        message = None
    return peer_id, user_id, message_id, message, attachments, timestamp, fwd_messages

def fwdParse(fwd):
    html="""<table border="1" width="100%" frame="hsides" style="margin-left:5px;">"""
    for i in fwd:
        user_name = getPeerName(i['from_id'])
        if i['from_id'] < 0:
            html+="""<tr><td>
<a href='https://vk.com/public{}' target="_blank">{}</a>
</td></tr>""".format(-i['from_id'],user_name)
        else:
            html+="""<tr><td>
<a href='https://vk.com/id{}' target="_blank">{}</a>
</td></tr>""".format(i['from_id'],user_name)
        if i['text'] != "":
            html+="<tr><td>"+i['text'].replace("<","&lt;").replace(">","&gt;").replace("\n","<br />")+"<br />"
        else:
            html+="<tr><td>"
        if i['attachments'] != []:
            html+=attachmentsParse(parseUrls(i['attachments']))
        if 'fwd_messages' in i:
            html+=fwdParse(i['fwd_messages'])
        elif 'reply_message' in i:
            html+=fwdParse([i['reply_message']])
        html+="</td></tr>"
        html+="<tr><td>{}</td></tr>".format(time.ctime(i['date']))
    html+="</table>"
    return html

def activityReport(message_id, isEdited=False, attachments=None, fwd=None,  message=None, hasUpdateTime=False):
    try:
        peer_name = user_name = oldMessage = oldAttachments = date = oldFwd = None
        cursor.execute("""SELECT * FROM messages WHERE message_id = ?""", (message_id,))
        fetch = cursor.fetchone()
        if not fetch[3] is None:
            oldMessage = str(fetch[3])
        if not attachments is None:
            attachments = parseUrls(json.loads(attachments))
        if not fwd is None:
            fwd = json.loads(fwd)
        if not fetch[4] is None:
            oldAttachments = parseUrls(json.loads(fetch[4]))
        if not fetch[6] is None:
            oldFwd = json.loads(fetch[6])
        row = """
            <tr>
                <td>"""
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
        peer_name = getPeerName(fetch[0])
        user_name = getPeerName(fetch[1])
        date = time.ctime(fetch[5])
        peer_id = fetch[0]
        user_id = fetch[1]
        del fetch
        row+="""{}</td>
                <td>""".format(str(message_id))
        if peer_id > 2000000000:
            row+="""
                    <a href='https://vk.com/im?sel=c{}' target="_blank">{}</a>
                </td>
                <td>""".format(str(peer_id-2000000000),peer_name)
        elif peer_id < 0:
            row+="""
                    <a href='https://vk.com/public{}' target="_blank">{}</a>
                </td>
                <td>""".format(str(-peer_id),peer_name)
        else:
            row+="""
                    <a href='https://vk.com/id{}' target="_blank">{}</a>
                </td>
                <td>""".format(str(peer_id),peer_name)
        if user_id < 0:
            row+="""
                    <a href='https://vk.com/public{}' target="_blank">{}</a>
                </td>""".format(str(-user_id),user_name)
        else:
            row+="""
                    <a href='https://vk.com/id{}' target="_blank">{}</a>
                </td>""".format(str(user_id),user_name)
        if isEdited:
            row+="""
                <td width="50%">
                    <b>Старое</b><br />
                    """
            if not oldMessage is None:
                row+=oldMessage.replace("<","&lt;").replace(">","&gt;").replace("\n","<br />")+"<br />"
            if not oldAttachments is None:
                row+="<b>Вложения</b><br />"+attachmentsParse(oldAttachments)+"<br />"
            if not oldFwd is None:
                row+="<b>Пересланное</b><br />"+fwdParse(oldFwd)
            row+="""
                </td>
                <td width="50%">
                    <b>Новое</b><br />
                    """
            if not message is None:
                row+=message.replace("<","&lt;").replace(">","&gt;").replace("\n","<br />")+"<br />"
            if not attachments is None:
                row+="<b>Вложения</b><br />"+attachmentsParse(attachments)+"<br />"
            if not fwd is None:
                row+="<b>Пересланное</b><br />"+fwdParse(fwd)
            row+="</td><td>"
            row+=date+"</td>"
        else:
            row+="""
                <td width="100%" colspan='2'><b>Удалено</b><br />
                """
            if not oldMessage is None:
                row+=oldMessage.replace("<","&lt;").replace(">","&gt;").replace("\n","<br />")+"<br />"
            if not oldAttachments is None:
                row+="<b>Вложения</b><br />"+attachmentsParse(oldAttachments)+"<br />"
            if not oldFwd is None:
                row+="<b>Пересланное</b><br />"+fwdParse(oldFwd)
            row+="</td>\n<td>"
            row+=date+"</td>"
    except BaseException as e:
        f = open(os.path.join(cwd, 'errorLog.txt'), 'a+')
        f.write(str(e)+" "+row+" "+time.ctime(time.time())+"\n\n")
        f.close()
    finally:
        row+="</tr>"
        messagesDump = messagesDump[:478]+row+messagesDump[478:]
        messagesActivities.write(messagesDump)
        messagesActivities.close()

stop = False
tableWatcher = threading.Thread(target=bgWatcher)
tableWatcher.start()

flags = (262144, 131072, 65536, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1)
sizes = ("s","m","x","o","p","q","r","y","z","w")
events = []

threading.Thread(target=predefinedActions).start()
tryAgainIfFailed(main, delay=5)
