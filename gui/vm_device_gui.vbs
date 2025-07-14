Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory of this script
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory and run the launcher
objShell.CurrentDirectory = strScriptDir
objShell.Run "pythonw.exe launcher.py", 0, False
