# VM Device GUI - Guest System Interface

A graphical user interface for managing USB device passthrough from within your virtual machine. This application connects to the host system via SSH to remotely control USB device attachment/detachment using the [vm-device CLI tool](../cli/README.md).

## Overview

This GUI application runs inside your virtual machine and provides a user-friendly interface for managing USB devices on the host system. It uses SSH to connect to your host system and execute the vm-device CLI commands remotely.

## Features

- **Graphical Interface**: Easy-to-use GUI with device lists and controls
- **System Tray Integration**: Minimize to system tray for background operation
- **SSH Connection**: Secure connection to host system using SSH aliases
- **Real-time Updates**: Live device status monitoring and updates
- **Silent Operation**: No command prompt windows when launched
- **Auto-reconnect**: Automatic reconnection of devices after disconnection
- **Configuration Management**: Persistent settings storage

## Quick Setup (Recommended)

Run the setup script to automatically create shortcuts and install dependencies:

```powershell
python setup.py
```

This will:
- Check Python installation
- Install required dependencies (paramiko, pystray, pillow)
- Create desktop shortcut
- Create Start Menu shortcut (silent operation)

## Manual Options

### Option 1: VBS Script (Silent - Recommended)
Double-click `vm_device_gui.vbs` to run the application silently without any command prompt window.

### Option 2: Batch File
Double-click `vm_device_gui.bat` to run the application (uses pythonw.exe to minimize console window).

### Option 3: PowerShell Script
Right-click `vm_device_gui.ps1` and select "Run with PowerShell" (runs hidden).

### Option 4: Python Launcher
Run `pythonw launcher.py` - includes better error handling and dependency checking.

### Option 5: Manual Silent Shortcut Creation
Run the PowerShell script to create a completely silent Start Menu shortcut:
```powershell
powershell -ExecutionPolicy Bypass -File create_silent_shortcut.ps1
```

## Creating an Executable (Advanced)

If you want to create a standalone executable, you can use PyInstaller:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create the executable:
   ```
   pyinstaller --onefile --windowed --icon=python.exe launcher.py
   ```

3. The executable will be created in the `dist` folder.

## Files Created

- `vm_device_gui.vbs` - Silent VBS script launcher (no command prompt)
- `vm_device_gui.bat` - Batch file launcher (uses pythonw.exe)
- `vm_device_gui.ps1` - PowerShell script launcher (hidden window)
- `launcher.py` - Python launcher with error handling
- `create_shortcut.ps1` - Creates Start Menu shortcut (pythonw.exe)
- `create_silent_shortcut.ps1` - Creates completely silent Start Menu shortcut (VBS)
- `setup.py` - Automated setup script (creates silent shortcuts)
- `README.md` - This file

## Usage

After running the setup, you can:
1. Find "VM Device GUI" in your Start Menu
2. Use the desktop shortcut (if created)
3. Run any of the launcher files directly

The application will start with the GUI and system tray support as configured in your original script.

## SSH Configuration

Before using the GUI, you need to configure SSH access to your host system:

### 1. Set up SSH Key Authentication

From your VM (guest system):

```bash
# Generate SSH key pair (if you don't have one)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# Copy public key to host system
ssh-copy-id username@host-ip-address
```

### 2. Configure SSH Host Alias

Create or edit `~/.ssh/config`:

```bash
Host vm-host
    HostName 192.168.1.100
    User your-username
    IdentityFile ~/.ssh/id_rsa
    Port 22
```

### 3. Test SSH Connection

```bash
ssh vm-host
```

### 4. Configure GUI Application

1. Launch the VM Device GUI
2. Click "Settings" 
3. Enter your SSH host alias (e.g., "vm-host")
4. Set the vm-device path on the host (e.g., "/home/user/.local/bin/vm-device")
5. Click "Save"
6. Click "Connect"

## Requirements

- Python 3.6 or higher
- SSH client (usually pre-installed)
- Network connectivity to host system
- SSH access to host system with vm-device CLI tool installed

## Dependencies

The following Python packages are required (installed automatically by setup.py):

- `paramiko` - SSH client library
- `pystray` - System tray integration
- `pillow` - Image processing for tray icons
