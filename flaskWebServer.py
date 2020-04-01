from functools import wraps
from flask import Flask, request, Response, send_from_directory
import json
import os
import time
cwd = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(cwd, 'config.json'), "r") as conf:
    config = json.load(conf)

app = Flask(__name__)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username in config['users'] and config['users'][username] == password

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper config', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if config['useAuth']:
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/")
@requires_auth
def index():
    fileList = list(filter(lambda i: i.find('mes') != -1,os.listdir(os.path.join(cwd,"mesAct"))))
    sortList=[i[:9]+i[13:15]+i[11:13]+i[9:11]+i[15:] for i in fileList]
    sortList = sorted(zip(sortList, fileList), key=lambda i: i[0])
    fileList = [i[1] for i in sortList]
    html = """<!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
    </head>
    <body>
        <ul>
            {}
        </ul>
    </body>
    </html>"""
    row = """<li><a href='{}'>{}</a></li>\n"""
    lis=""
    for i in fileList:
        lis+=row.format(i,time.strftime("%d %B %Y",time.strptime(i[9:15],"%d%m%y")))
    html = html.format(lis)
    return html

@app.route('/<path:path>')
@requires_auth
def send(path):
    return send_from_directory('mesAct', path)

@app.route("/vkGetVideoLink.html")
def video():
    if config['useAuth']:
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper config', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})
        else:
            return """<!DOCTYPE html>
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
    </html>""".format(config['ACCESS_TOKEN'] if list(config['users']).index(auth.username) == 0 else "")
    else:
        return send_from_directory('mesAct', 'vkGetVideoLink.html')

if __name__ == "__main__":
    app.run()