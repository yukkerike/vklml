import vk_api
import json
import sqlite3
import os

cwd = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(cwd, "config.json"), 'r') as conf:
	config = json.load(conf)

vk_session = vk_api.VkApi(token=config['ACCESS_TOKEN'],api_version='5.130')
vk = vk_session.get_api()

conn = sqlite3.connect(
	os.path.join(cwd, "messages.db"),
	check_same_thread=False,
	timeout=15.0
)
cursor = conn.cursor()

cursor.execute("""SELECT user_id FROM users_cache""")
users = [i[0] for i in cursor.fetchall()]
users = [','.join(map(str,users[i:i+1000])) for i in range(0,len(users),1000)]
for i in users:
	list = vk.users.get(user_ids=i)
	for j in list:
		cursor.execute("""UPDATE users_cache SET user_name = ? WHERE user_id = ?""", (f"{j['first_name']} {j['last_name']}",j['id'],))

cursor.execute("""SELECT chat_id FROM chats_cache""")
chats = [i[0] for i in cursor.fetchall()]
chats = [','.join(map(str,chats[i:i+100])) for i in range(0,len(chats),100)]
for i in chats:
	list = vk.messages.getConversationsById(peer_ids=i)
	for j in list['items']:
		cursor.execute("""UPDATE chats_cache SET chat_name = ? WHERE chat_id = ?""", (j['chat_settings']['title'],j['peer']['id'],))

conn.commit()
cursor.close()