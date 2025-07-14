#!/usr/bin/env python3
"""
VM Device GUI Setup Script
Sets up the VM Device GUI application for easy access from Windows Start Menu.
"""
import os
import sys
import subprocess
import winreg
from pathlib import Path

def create_desktop_shortcut():
    """Create a desktop shortcut."""
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "VM Device GUI.lnk"
    
    ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"{Path(__file__).parent / 'vm_device_gui.vbs'}`""
$Shortcut.WorkingDirectory = "{Path(__file__).parent}"
$Shortcut.IconLocation = "pythonw.exe,0"
$Shortcut.Description = "VM USB Device Manager"
$Shortcut.WindowStyle = 1
$Shortcut.Save()
'''
    
    try:
        subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
        print(f"✓ Desktop shortcut created: {shortcut_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create desktop shortcut: {e}")
        return False

def create_start_menu_shortcut():
    """Create a Start Menu shortcut."""
    start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    shortcut_path = start_menu / "VM Device GUI.lnk"
    
    ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"{Path(__file__).parent / 'vm_device_gui.vbs'}`""
$Shortcut.WorkingDirectory = "{Path(__file__).parent}"
$Shortcut.IconLocation = "pythonw.exe,0"
$Shortcut.Description = "VM USB Device Manager"
$Shortcut.WindowStyle = 1
$Shortcut.Save()
'''
    
    try:
        subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
        print(f"✓ Start Menu shortcut created: {shortcut_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create Start Menu shortcut: {e}")
        return False

def check_python_installation():
    """Check if Python is properly installed and accessible."""
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Python found: {result.stdout.strip()}")
            return True
        else:
            print("✗ Python not found in PATH")
            return False
    except FileNotFoundError:
        print("✗ Python not found in PATH")
        return False

def install_dependencies():
    """Install required Python dependencies."""
    dependencies = ["paramiko", "pystray", "pillow"]
    
    print("Installing dependencies...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✓ {dep} installed")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {dep}")
            return False
    
    return True

def main():
    print("VM Device GUI Setup")
    print("=" * 20)
    
    # Check Python installation
    if not check_python_installation():
        print("\nPlease install Python and ensure it's in your PATH.")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\nFailed to install dependencies. Please run manually:")
        print("pip install paramiko pystray pillow")
        return 1
    
    # Create shortcuts
    print("\nCreating shortcuts...")
    desktop_ok = create_desktop_shortcut()
    start_menu_ok = create_start_menu_shortcut()
    
    if desktop_ok or start_menu_ok:
        print("\n✓ Setup completed successfully!")
        print("You can now run 'VM Device GUI' from:")
        if desktop_ok:
            print("  - Desktop shortcut")
        if start_menu_ok:
            print("  - Start Menu")
    else:
        print("\n✗ Setup failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
