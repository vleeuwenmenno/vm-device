#!/usr/bin/env python3
"""
VM Device GUI Launcher
Ensures proper startup and error handling for the VM Device GUI application.
"""
import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import paramiko
        import pystray
        from PIL import Image
        return True
    except ImportError as e:
        return False, str(e)

def main():
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check dependencies
    deps_result = check_dependencies()
    if deps_result is not True:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(
            "Missing Dependencies", 
            f"Required Python packages are missing:\n{deps_result[1]}\n\n"
            f"Please install them with:\npip install paramiko pystray pillow"
        )
        root.destroy()
        return 1
    
    # Import and run the main application
    try:
        from vm_device_gui import VMDeviceGUI
        app = VMDeviceGUI()
        app.mainloop()
        return 0
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start application:\n{str(e)}")
        root.destroy()
        return 1

if __name__ == "__main__":
    sys.exit(main())
