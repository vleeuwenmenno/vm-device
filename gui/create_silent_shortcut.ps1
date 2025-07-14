$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\VM Device GUI.lnk")
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$PSScriptRoot\vm_device_gui.vbs`""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "pythonw.exe,0"
$Shortcut.Description = "VM USB Device Manager"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host "Silent shortcut created in Start Menu: VM Device GUI"
Write-Host "This shortcut will run without showing any command prompt window"
