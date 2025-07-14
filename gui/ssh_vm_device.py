import subprocess
import json

class SSHVMDeviceClient:
    def __init__(self, ssh_host_alias, vm_device_path="~/.local/bin/vm-device", sudo_password=None):
        self.ssh_host = ssh_host_alias
        self.vm_device_path = vm_device_path
        self.sudo_password = sudo_password

    def set_sudo_password(self, password):
        self.sudo_password = password
        # Run sudo -v to cache credentials on the remote host
        ssh_command = [
            "ssh",
            self.ssh_host,
            f"echo '{self.sudo_password}' | sudo -S -v"
        ]
        try:
            subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                timeout=10
            )
        except Exception:
            pass

    def _run_ssh_command(self, args, use_sudo=True):
        """
        Run a command on the remote host via SSH and return parsed JSON output.
        If use_sudo is True, always use sudo (with or without password).
        """
        if use_sudo:
            if self.sudo_password:
                remote_cmd = f"echo '{self.sudo_password}' | sudo -S {self.vm_device_path} {' '.join(args)}"
            else:
                remote_cmd = f"sudo {self.vm_device_path} {' '.join(args)}"
        else:
            remote_cmd = f"{self.vm_device_path} {' '.join(args)}"
        ssh_command = [
            "ssh",
            self.ssh_host,
            remote_cmd
        ]
        try:
            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return {"error": result.stderr.strip(), "success": False}
            # Try to parse JSON from stdout
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output", "raw_output": result.stdout, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def list_attached(self):
        return self._run_ssh_command(["--list", "--json"], use_sudo=True)

    def list_available(self):
        # Listing available devices may not require sudo, but can be changed if needed
        return self._run_ssh_command(["--list-available", "--json"], use_sudo=True)

    def attach_device(self, vendor, product):
        return self._run_ssh_command(["--attach", f"{vendor}:{product}", "--json"], use_sudo=True)

    def detach_device(self, vendor, product):
        return self._run_ssh_command(["--detach", f"{vendor}:{product}", "--json"], use_sudo=True)

    def reconnect_device(self, vendor, product):
        return self._run_ssh_command(["--reconnect", f"{vendor}:{product}", "--json"], use_sudo=True)