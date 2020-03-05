Set oShell = CreateObject ("Wscript.Shell") 
Dim strArgs
strArgs = "cmd /c py C:\Users\ra1n\vkCacheBot\vkLongpollLogger.py"
oShell.Run strArgs, 0, false