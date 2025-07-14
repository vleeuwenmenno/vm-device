$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\VM Device GUI.lnk")
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "`"$PSScriptRoot\launcher.py`""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "pythonw.exe,0"
$Shortcut.Description = "VM USB Device Manager"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host "Shortcut created in Start Menu: VM Device GUI"
Write-Host "You can now find 'VM Device GUI' in your Start Menu"
