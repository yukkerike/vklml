import time
import os
import threading

def generateIndex(cwd, date):
    f = open(os.path.join(cwd, "mesAct", "index.html"), 'w')
    messageList = ""
    for i in range(1, 32):
        messageList += """
        <li class="list-group-item"><a href="./messages_"""+str(i).center(2, "0")+"""{0}.html" class="stretched-link">messages_"""+str(i).center(2, "0")+"""{0}.html</a></li>"""
    f.write(("""<!--{0}-->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <link rel="stylesheet" href="./bootstrap.css">
</head>
<body>
    <ul class="list-group">"""+messageList+"""
    </ul>
    <script>
        list = document.getElementsByTagName("li")
        var now = new Date().getDate()
        for (i = 30; i >= now; i--) list[i].setAttribute("hidden","");
    </script>
</body>
</html>""").format(date))
    f.close()

class indexUpdater:
    def updateIndex(self, cwd, standalone=0):
        date = time.strftime("%m%y", time.localtime())
        if standalone == 1:
            generateIndex(cwd, date)
        elif standalone == 0:
            while True:
                if not os.path.exists(os.path.join(cwd, "mesAct", "index.html")):
                    generateIndex(cwd, date)
                else:
                    f = open(os.path.join(cwd, "mesAct", "index.html"), 'r')
                    prevDate = f.read()[4:9]
                    f.close()
                    if prevDate != date:
                        generateIndex(cwd, date)
                time.sleep(86400)


    def __init__(self, standalone=0):
        cwd = os.path.dirname(os.path.abspath(__file__))
        threading.Thread(target=self.updateIndex, args=(cwd, standalone,)).start()

if __name__ == "__main__":
    indexUpdater(1)
