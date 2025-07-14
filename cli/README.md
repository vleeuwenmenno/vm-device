# vm-device CLI Tool

A command-line tool for managing USB device passthrough to KVM/QEMU virtual machines using libvirt.

## Overview

The `vm-device` script allows you to easily attach, detach, and manage USB devices for your KVM/QEMU virtual machines. It provides both interactive and non-interactive modes, with JSON output support for automation.

## Features

- **List attached devices**: Show USB devices currently attached to your VM
- **List available devices**: Show USB devices available for attachment
- **Attach devices**: Add USB devices to your VM (interactive or by ID)
- **Detach devices**: Remove USB devices from your VM
- **Reconnect devices**: Refresh device connections 
- **Cleanup**: Remove duplicate USB hostdev entries
- **JSON output**: Machine-readable output for automation
- **Interactive mode**: User-friendly prompts for device selection

## Prerequisites

- Linux host system with KVM/QEMU
- libvirt and virsh installed
- Virtual machine configured with libvirt
- sudo privileges for virsh operations

## Installation

1. Copy the `vm-device` script to your preferred location (e.g., `~/.local/bin/`)
2. Make it executable: `chmod +x vm-device`
3. Edit the `VM_NAME` variable in the script to match your VM name
4. Optionally add the script location to your PATH

## Configuration

Edit the script to set your VM name:

```bash
VM_NAME="your-vm-name"
```

You can find your VM name with: `virsh list --all`

## Usage

### Basic Commands

```bash
# List currently attached USB devices
./vm-device --list

# List available USB devices for attachment
./vm-device --list-available

# Attach a device interactively
./vm-device --attach

# Detach a device interactively  
./vm-device --detach

# Reconnect a device interactively
./vm-device --reconnect

# Clean up duplicate entries
./vm-device --cleanup
```

### Device-Specific Commands

```bash
# Attach specific device by vendor:product ID
./vm-device --attach 046d:c52b

# Detach specific device
./vm-device --detach 046d:c52b

# Reconnect specific device
./vm-device --reconnect 046d:c52b
```

### JSON Output

Add `--json` to any command for machine-readable output:

```bash
# List attached devices in JSON format
./vm-device --list --json

# List available devices in JSON format  
./vm-device --list-available --json

# Attach device with JSON output
./vm-device --attach 046d:c52b --json
```

### Help

```bash
./vm-device --help
```

## Device Status

The tool reports devices in several states:

- **Actively Attached**: Device is properly connected to the VM
- **Available**: Device is on the host but not attached to VM
- **Disconnected**: Device was configured but is no longer available

## Example Output

```
Currently attached USB devices to win11-vm:
+-----+------------+-------------+--------------------------------+--------------+
| Num | Vendor ID  | Product ID  | Device Name                    | Status       |
+-----+------------+-------------+--------------------------------+--------------+
| 1   | 046d       | c52b        | Logitech Unifying Receiver     | Available    |
| 2   | 18a5       | 0243        | Verbatim Flash Drive           | Disconnected |
+-----+------------+-------------+--------------------------------+--------------+
```

## JSON API

The JSON output provides structured data for automation:

```json
{
  "attached_devices": [
    {
      "vendor": "046d",
      "product": "c52b", 
      "name": "Logitech Unifying Receiver",
      "status": "Actively Attached"
    }
  ],
  "summary": {
    "disconnected": 0,
    "available": 1,
    "actively_attached": 1,
    "total": 2
  }
}
```

## Integration with GUI Client

This CLI tool is designed to work with the VM Device GUI client. The GUI client (typically running in your VM) connects to the host system via SSH to execute these commands remotely.

To set up SSH access for the GUI client:

1. Configure SSH key authentication from your VM to the host
2. Set up SSH host aliases in your VM's `~/.ssh/config`
3. Ensure the vm-device script is in the PATH or specify the full path in the GUI client

## Troubleshooting

### Permission Issues
Make sure your user has sudo privileges and can execute virsh commands:
```bash
sudo virsh list
```

### VM Not Found
Check that your VM name is correct:
```bash
virsh list --all
```

### Device Not Appearing
If a device doesn't appear after attachment:
1. Check that the device is not in use by the host
2. Try reconnecting the device
3. Restart the VM if necessary

## Device ID Format

Device IDs use the format `VENDOR:PRODUCT` where both are 4-digit hexadecimal values from lsusb output.

Example: `046d:c52b` for a Logitech Unifying Receiver

## Notes

- Device attachments are persistent and survive VM reboots
- The tool requires the VM to be running for live attachment/detachment
- Some devices may require specific drivers in the guest OS
- USB hubs and root hubs are automatically filtered out
