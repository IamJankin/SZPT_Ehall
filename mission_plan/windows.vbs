On Error Resume Next

Set ws = WScript.Createobject("WScript.Shell")

ws.run "cmd /c ""python D:\SZPT_Ehall\SZPT_Ehall.py""",0 ,true 