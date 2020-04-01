import time
import os
import threading

class indexUpdater:
    def updateIndex(self,cwd,standalone=0):
        date = time.strftime("%m%y",time.localtime())
        if standalone == 1:
            self.generateIndex(cwd, date)
        elif standalone == 0:
            while True:
                if not os.path.exists(os.path.join(cwd, "mesAct",  "index.html")):
                    self.generateIndex(cwd, date)
                else:
                    f = open(os.path.join(cwd, "mesAct",  'index.html'), 'r')
                    prevDate = f.read()[4:9]
                    if prevDate != date:
                        f.close()
                        self.generateIndex(cwd, date)    
                time.sleep(86400)
                
    def generateIndex(self, cwd, date):
        f = open(os.path.join(cwd, "mesAct",  'index.html'), 'w')
        messageList = ""
        for i in range(1,32):
            messageList += """
            <li><a href="./messages_"""+str(i).center(2,"0")+"""{0}.html">messages_"""+str(i).center(2,"0")+"""{0}.html</a></li>"""
        f.write(("""<!--{0}-->
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
    </head>
    <body>
        <ul>"""+messageList+"""
        </ul>
        <script>
            list = document.getElementsByTagName("li")
            var now = new Date().getDate()
            for (i = 30; i >= now; i--) list[i].setAttribute("hidden","");
        </script>
    </body>
</html>""").format(date))
        f.close()

    def __init__(self,standalone=0):
        cwd = os.path.dirname(os.path.abspath(__file__))
        threading.Thread(target=self.updateIndex,args=(cwd,standalone,)).start()


if __name__ == "__main__":
    b = indexUpdater(1)
