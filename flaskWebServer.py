import json
import os
import time
import logging
import logging.handlers
from functools import wraps
from flask import Flask, request, Response, send_from_directory, make_response
import locale

cwd = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(cwd, 'config.json'), "r") as conf:
    config = json.load(conf)
firstUser = list(config['users'])[0]
html = """<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <link rel="stylesheet" href="./bootstrap.css">
</head>
<body>
    <ul class="list-group">{}
    </ul>
</body>
</html>"""
row = "\n        <li class='list-group-item'><a href='{}' class='stretched-link'>{}</a></li>"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(os.path.join(cwd, 'log.txt'), maxBytes=102400)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

app = Flask(__name__, static_folder=os.path.join(cwd, 'mesAct', 'static'))

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
    def requires_auth_decorated(*args, **kwargs):
        if config['useAuth']:
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
            if auth.username != firstUser:
                logger.info("Запрос от %s", auth.username)
        return f(*args, **kwargs)
    return requires_auth_decorated

def no_cache(f):
    @wraps(f)
    def no_cache_decorated(*args, **kwargs):
        response = f(*args, **kwargs)
        if not 'Expires' in response.headers:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            response.headers['Cache-Control'] = 'public, max-age=0'
        return response
    return no_cache_decorated

@app.route("/favicon.ico")
def favicon():
    return Response(200)

@app.route("/bootstrap.css")
def push_bootstrap():
    return send_from_directory('mesAct', 'bootstrap.css')

@app.route("/")
@requires_auth
@no_cache
def index():
    fileList = list(
        filter(
            lambda i: i.find('mes') != -1,
            os.listdir(os.path.join(
                    cwd,
                    "mesAct"
            ))
        )
    )
    sortList = [f"{i[:9]}{i[13:15]}{i[11:13]}{i[9:11]}{i[15:]}" for i in fileList]
    sortList = sorted(
        zip(sortList, fileList),
        key=lambda i: i[0]
    )
    fileList = [i[1] for i in sortList]
    lis = ""
    locale.setlocale(locale.LC_ALL, '')
    curr_date = time.strftime("%d %B %Y")
    for i in fileList:
        file_date = time.strftime(
            "%d %B %Y",
            time.strptime(i[9:15], "%d%m%y")
        )
        cache_flag = file_date == curr_date
        lis += row.format(f"./{i}", file_date)
    r = make_response(html.format(lis))
    locale.setlocale(locale.LC_ALL, 'C')
    if cache_flag:
        t_delta = list(time.localtime())
        t_delta[2]+=1
        t_delta[3] = t_delta[4] = t_delta[5] = 0
        t_midnight = t_delta
        t_delta = str(int(time.mktime(tuple(t_delta)) - time.time()))
        r.headers['Cache-Control'] = 'public, max-age=' + t_delta
        r.headers['Expires'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", tuple(t_midnight))
    return r

@app.route('/<path:path>')
@requires_auth
@no_cache
def send(path):
    cache_flag = path[9:15] != time.strftime("%d%m%y")
    r = send_from_directory("mesAct", path)
    del r.headers['Expires']
    if cache_flag:
        r.headers['Cache-Control'] = 'public, max-age=604800'
        r.headers['Expires'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(time.time() + 604800))
    return r

@app.route('/static/')
@no_cache
def staticfileslist():
    if os.path.exists(os.path.join(cwd, "mesAct", 'static')):
        return make_response(html.format('\n'.join(map(
            lambda i: row.format(f"./{i}", i),
            os.listdir(os.path.join(
                cwd,
                "mesAct",
                "static"))))
        ))
    return make_response('Static folder not found')

@app.route("/vkGetVideoLink.html")
def video():
    if config['useAuth']:
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper config', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})
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
    </html>""".format(config['tokenToPlaceInGetVideo'] if config['tokenToPlaceInGetVideo'] != "" else config['ACCESS_TOKEN'] if auth.username == firstUser else "")
    return send_from_directory("mesAct", 'vkGetVideoLink.html')

if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0')
