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
                f.write("""<!--{0}-->
        <!DOCTYPE html>
        <html>
        <head
                <meta charset="utf-8">
        </head>
        <body>
                <ul>
                        <li><a href="./messages_01{0}.html">messages_01{0}.html</a></li>
                        <li><a href="./messages_02{0}.html">messages_02{0}.html</a></li>
                        <li><a href="./messages_03{0}.html">messages_03{0}.html</a></li>
                        <li><a href="./messages_04{0}.html">messages_04{0}.html</a></li>
                        <li><a href="./messages_05{0}.html">messages_05{0}.html</a></li>
                        <li><a href="./messages_06{0}.html">messages_06{0}.html</a></li>
                        <li><a href="./messages_07{0}.html">messages_07{0}.html</a></li>
                        <li><a href="./messages_08{0}.html">messages_08{0}.html</a></li>
                        <li><a href="./messages_09{0}.html">messages_09{0}.html</a></li>
                        <li><a href="./messages_10{0}.html">messages_10{0}.html</a></li>
                        <li><a href="./messages_11{0}.html">messages_11{0}.html</a></li>
                        <li><a href="./messages_12{0}.html">messages_12{0}.html</a></li>
                        <li><a href="./messages_13{0}.html">messages_13{0}.html</a></li>
                        <li><a href="./messages_14{0}.html">messages_14{0}.html</a></li>
                        <li><a href="./messages_15{0}.html">messages_15{0}.html</a></li>
                        <li><a href="./messages_16{0}.html">messages_16{0}.html</a></li>
                        <li><a href="./messages_17{0}.html">messages_17{0}.html</a></li>
                        <li><a href="./messages_18{0}.html">messages_18{0}.html</a></li>
                        <li><a href="./messages_19{0}.html">messages_19{0}.html</a></li>
                        <li><a href="./messages_20{0}.html">messages_20{0}.html</a></li>
                        <li><a href="./messages_21{0}.html">messages_21{0}.html</a></li>
                        <li><a href="./messages_22{0}.html">messages_22{0}.html</a></li>
                        <li><a href="./messages_23{0}.html">messages_23{0}.html</a></li>
                        <li><a href="./messages_24{0}.html">messages_24{0}.html</a></li>
                        <li><a href="./messages_25{0}.html">messages_25{0}.html</a></li>
                        <li><a href="./messages_26{0}.html">messages_26{0}.html</a></li>
                        <li><a href="./messages_27{0}.html">messages_27{0}.html</a></li>
                        <li><a href="./messages_28{0}.html">messages_28{0}.html</a></li>
                        <li><a href="./messages_29{0}.html">messages_29{0}.html</a></li>
                        <li><a href="./messages_30{0}.html">messages_30{0}.html</a></li>
                        <li><a href="./messages_31{0}.html">messages_31{0}.html</a></li>
                </ul>
                <script>
                        list = document.getElementsByTagName("li")
                        var now = new Date().getDate()
                        for (i = 30; i >= now; i--) list[i].setAttribute("hidden","");
                </script>
        </body>
        </html>""".format(date))
                f.close()

        def __init__(self,standalone=0):
                cwd = os.path.dirname(os.path.abspath(__file__))
                threading.Thread(target=self.updateIndex,args=(cwd,standalone,)).start()


if __name__ == "__main__":
        b = indexUpdater(1)
