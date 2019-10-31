import time
import os
def updateIndex(cwd):
        date = time.strftime("%d%m%y",time.localtime())
        if not os.path.exists(os.path.join(cwd, "mesAct",  "index.html")):
                generateIndex(cwd, date)
        else:
                f = open(os.path.join(cwd, "mesAct",  'index.html'), 'r')
                if f.read()[4:9] != date[2:]:
                        f.close()
                        generateIndex(cwd, date)

def generateIndex(cwd, date):
        f = open(os.path.join(cwd, "mesAct",  'index.html'), 'w')
        f.write("""<!--{0}-->
<!DOCTYPE html>
<html>
<head
        <meta charset="utf-8">
</head>
<body>
        <ul>
                <li hidden><a href="./messages_01{0}.html">messages_01{0}.html</a></li>
                <li hidden><a href="./messages_02{0}.html">messages_02{0}.html</a></li>
                <li hidden><a href="./messages_03{0}.html">messages_03{0}.html</a></li>
                <li hidden><a href="./messages_04{0}.html">messages_04{0}.html</a></li>
                <li hidden><a href="./messages_05{0}.html">messages_05{0}.html</a></li>
                <li hidden><a href="./messages_06{0}.html">messages_06{0}.html</a></li>
                <li hidden><a href="./messages_07{0}.html">messages_07{0}.html</a></li>
                <li hidden><a href="./messages_08{0}.html">messages_08{0}.html</a></li>
                <li hidden><a href="./messages_09{0}.html">messages_09{0}.html</a></li>
                <li hidden><a href="./messages_10{0}.html">messages_10{0}.html</a></li>
                <li hidden><a href="./messages_11{0}.html">messages_11{0}.html</a></li>
                <li hidden><a href="./messages_12{0}.html">messages_12{0}.html</a></li>
                <li hidden><a href="./messages_13{0}.html">messages_13{0}.html</a></li>
                <li hidden><a href="./messages_14{0}.html">messages_14{0}.html</a></li>
                <li hidden><a href="./messages_15{0}.html">messages_15{0}.html</a></li>
                <li hidden><a href="./messages_16{0}.html">messages_16{0}.html</a></li>
                <li hidden><a href="./messages_17{0}.html">messages_17{0}.html</a></li>
                <li hidden><a href="./messages_18{0}.html">messages_18{0}.html</a></li>
                <li hidden><a href="./messages_19{0}.html">messages_19{0}.html</a></li>
                <li hidden><a href="./messages_20{0}.html">messages_20{0}.html</a></li>
                <li hidden><a href="./messages_21{0}.html">messages_21{0}.html</a></li>
                <li hidden><a href="./messages_22{0}.html">messages_22{0}.html</a></li>
                <li hidden><a href="./messages_23{0}.html">messages_23{0}.html</a></li>
                <li hidden><a href="./messages_24{0}.html">messages_24{0}.html</a></li>
                <li hidden><a href="./messages_25{0}.html">messages_25{0}.html</a></li>
                <li hidden><a href="./messages_26{0}.html">messages_26{0}.html</a></li>
                <li hidden><a href="./messages_27{0}.html">messages_27{0}.html</a></li>
                <li hidden><a href="./messages_28{0}.html">messages_28{0}.html</a></li>
                <li hidden><a href="./messages_29{0}.html">messages_29{0}.html</a></li>
                <li hidden><a href="./messages_30{0}.html">messages_30{0}.html</a></li>
                <li hidden><a href="./messages_31{0}.html">messages_31{0}.html</a></li>
        </ul>
        <script>
                list = document.getElementsByTagName("li")
                for (i = 0; i < {1}; i++) list[i].removeAttribute("hidden");
        </script>
</body>
</html>""".format(date[2:],date[:2]))
        f.close()

if __name__ == "__main__":
        cwd = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(os.path.join(cwd, "mesAct")):
                os.makedirs(os.path.join(cwd, "mesAct"))
        updateIndex(cwd)
