# VM Device Manager

A vibe coded :3 comprehensive solution for managing USB device passthrough between KVM/QEMU virtual machines and their host systems. This project provides both a command-line interface for the host system and a graphical user interface for the guest system.

## Architecture

This project consists of two main components:

### 🖥️ **Host System (CLI)** - [`cli/`](cli/README.md)
The command-line tool that runs on your Linux host system with KVM/QEMU. It manages USB device passthrough using libvirt/virsh commands.

- **Location**: Host system running your VMs
- **Technology**: Bash shell script with libvirt/virsh
- **Purpose**: Direct USB device management for KVM/QEMU VMs
- **Access**: Local command-line interface

### 🖼️ **Guest System (GUI)** - [`gui/`](gui/README.md)
The graphical user interface that runs inside your virtual machine. It connects to the host system via SSH to remotely manage USB devices.

- **Location**: Inside your VM (guest system)
- **Technology**: Python with Tkinter GUI and system tray support
- **Purpose**: User-friendly interface for remote USB management
- **Access**: SSH connection to host system

## How It Works

```
┌─────────────────────┐    SSH Connection    ┌─────────────────────┐
│   Guest VM (GUI)    │ ──────────────────→  │   Host System (CLI) │
│                     │                      │                     │
│  • Python GUI       │                      │  • vm-device script │
│  • System tray      │                      │  • libvirt/virsh    │
│  • SSH client       │                      │  • USB management   │
│                     │                      │                     │
│  User clicks        │                      │  Device attached    │
│  "Attach Device"    │                      │  to VM via libvirt  │
└─────────────────────┘                      └─────────────────────┘
```

## Quick Start

### 1. Set up the Host System (CLI)

1. Install on your Linux host running KVM/QEMU:
   ```bash
   cd cli/
   chmod +x vm-device
   # Edit VM_NAME in the script to match your VM
   ./vm-device --help
   ```

2. See detailed setup instructions: [**CLI README**](cli/README.md)

### 2. Set up the Guest System (GUI)

1. Install inside your VM:
   ```bash
   cd gui/
   python3 setup.py  # Installs dependencies and creates shortcuts
   ```

2. Configure SSH connection to your host system
3. See detailed setup instructions: [**GUI README**](gui/README.md)

## Features

### CLI Features (Host)
- List attached/available USB devices
- Attach/detach devices to/from VM
- Reconnect devices after disconnection
- JSON output for automation
- Interactive and non-interactive modes
- Persistent device configuration

### GUI Features (Guest)
- User-friendly graphical interface
- System tray integration
- Real-time device status monitoring
- Remote SSH connection management
- Silent operation (no command prompts)
- Auto-reconnect capabilities

## Requirements

### Host System
- Linux with KVM/QEMU virtualization
- libvirt and virsh installed
- sudo privileges for VM management
- SSH server running (for GUI client access)

### Guest System
- Python 3.6+
- SSH client capability
- Network connection to host system
- Required Python packages (installed automatically):
  - `paramiko` (SSH client)
  - `pystray` (system tray)
  - `pillow` (image processing)

## Configuration

### SSH Setup
The GUI client connects to the host via SSH. Set up SSH key authentication:

1. **On the guest system** (VM), generate SSH keys:
   ```bash
   ssh-keygen -t rsa -b 4096
   ```

2. **Copy public key to host**:
   ```bash
   ssh-copy-id user@host-system
   ```

3. **Configure SSH host alias** in `~/.ssh/config`:
   ```
   Host vm-host
       HostName 192.168.1.100
       User your-username
       IdentityFile ~/.ssh/id_rsa
   ```

4. **Test connection**:
   ```bash
   ssh vm-host
   ```

## Project Structure

```
vm-device/
├── README.md           # This file
├── cli/
│   ├── README.md      # CLI documentation
│   └── vm-device      # Host system script
└── gui/
    ├── README.md      # GUI documentation
    ├── setup.py       # Automated setup script
    ├── launcher.py    # GUI launcher with error handling
    ├── vm_device_gui.py      # Main GUI application
    ├── ssh_vm_device.py      # SSH client wrapper
    ├── tray_support.py       # System tray integration
    └── *.bat, *.ps1, *.vbs  # Windows launchers
```

## Getting Started

1. **Read the documentation**:
   - [CLI Setup Guide](cli/README.md) - For the host system
   - [GUI Setup Guide](gui/README.md) - For the guest system

2. **Set up the host system first** (CLI component)
3. **Then set up the guest system** (GUI component)  
4. **Configure SSH authentication** between guest and host
5. **Test the connection** and start managing your USB devices!

## License

This project is provided as-is for educational and personal use.

---

**Quick Links:**
- [📋 CLI Documentation](cli/README.md) - Host system setup
- [🖼️ GUI Documentation](gui/README.md) - Guest system setup
- [🔧 Troubleshooting](cli/README.md#troubleshooting) - Common issues and solutions
