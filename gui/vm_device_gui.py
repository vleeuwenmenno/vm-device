import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ssh_vm_device import SSHVMDeviceClient

import os
import configparser
from tray_support import TrayManager

class VMDeviceGUI(tk.Tk):
    CONFIG_PATH = os.path.expanduser("~/.config/vm-device-gui.conf")

    def __init__(self):
        super().__init__()
        self.title("VM USB Device Manager")
        self.geometry("700x400")

        self.ssh_host_var = tk.StringVar()
        self.vm_device_path_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.client = None
        self.sudo_password = None

        self.tray_manager = TrayManager(self)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Unmap>", self._on_minimize)

        self._load_config()
        self._build_connection_panel()
        self._build_tabs()
        self._build_status_bar()

        # Auto connect on startup if alias is set
        if self.ssh_host_var.get():
            self.after(100, self.connect_ssh)

    def _open_settings_dialog(self):
        win = tk.Toplevel(self)
        win.title("Settings")
        win.geometry("350x200")
        win.grab_set()
        tk.Label(win, text="SSH Host Alias:").pack(pady=10)
        alias_var = tk.StringVar(value=self.ssh_host_var.get())
        entry = tk.Entry(win, textvariable=alias_var, width=25)
        entry.pack(pady=5)
        tk.Label(win, text="vm-device path:").pack(pady=10)
        path_var = tk.StringVar(value=self.vm_device_path_var.get() or "~/.local/bin/vm-device")
        path_entry = tk.Entry(win, textvariable=path_var, width=30)
        path_entry.pack(pady=5)
        entry.focus_set()

        def save():
            self.ssh_host_var.set(alias_var.get())
            self.vm_device_path_var.set(path_var.get())
            self._save_config()
            win.destroy()

        tk.Button(win, text="Save", command=save).pack(pady=10)
        self.wait_window(win)

    def _load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.CONFIG_PATH):
            config.read(self.CONFIG_PATH)
            if "main" in config:
                if "ssh_alias" in config["main"]:
                    self.ssh_host_var.set(config["main"]["ssh_alias"])
                if "vm_device_path" in config["main"]:
                    self.vm_device_path_var.set(config["main"]["vm_device_path"])

    def _save_config(self):
        config = configparser.ConfigParser()
        config["main"] = {
            "ssh_alias": self.ssh_host_var.get(),
            "vm_device_path": self.vm_device_path_var.get() or "~/.local/bin/vm-device"
        }
        os.makedirs(os.path.dirname(self.CONFIG_PATH), exist_ok=True)
        with open(self.CONFIG_PATH, "w") as f:
            config.write(f)

    def prompt_sudo_password(self):
        pw_win = tk.Toplevel(self)
        pw_win.title("Sudo Password Required")
        pw_win.geometry("300x120")
        pw_win.grab_set()
        tk.Label(pw_win, text="Enter your sudo password:").pack(pady=10)
        pw_var = tk.StringVar()
        pw_entry = tk.Entry(pw_win, textvariable=pw_var, show="*", width=25)
        pw_entry.pack(pady=5)
        pw_entry.focus_set()
        result = {"password": None}

        def submit(event=None):
            result["password"] = pw_var.get()
            pw_win.destroy()

        pw_entry.bind("<Return>", submit)
        tk.Button(pw_win, text="OK", command=submit).pack(pady=10)
        self.wait_window(pw_win)
        return result["password"]

    def _build_connection_panel(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(frame, text="Settings", command=self._open_settings_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Connect", command=self.connect_ssh).pack(side=tk.LEFT, padx=5)

    def _build_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Attached Devices Tab
        self.attached_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.attached_frame, text="Attached Devices")
        self.attached_tree = self._build_device_table(self.attached_frame)
        btn_frame1 = ttk.Frame(self.attached_frame)
        btn_frame1.pack(fill=tk.X, pady=5)
        self.detach_btn = ttk.Button(btn_frame1, text="Detach", command=self.detach_selected, state=tk.DISABLED)
        self.detach_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame1, text="Refresh", command=self.refresh_attached).pack(side=tk.RIGHT, padx=5)
        self.attached_tree.bind("<<TreeviewSelect>>", self._on_attached_select)
        
        # Available Devices Tab
        self.available_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.available_frame, text="Available Devices")
        self.available_tree = self._build_device_table(self.available_frame)
        btn_frame2 = ttk.Frame(self.available_frame)
        btn_frame2.pack(fill=tk.X, pady=5)
        self.attach_btn = ttk.Button(btn_frame2, text="Attach", command=self.attach_selected, state=tk.DISABLED)
        self.attach_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="Refresh", command=self.refresh_available).pack(side=tk.RIGHT, padx=5)
        self.available_tree.bind("<<TreeviewSelect>>", self._on_available_select)

    def _build_device_table(self, parent):
        columns = ("vendor", "product", "name", "status")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col.capitalize())
            tree.column(col, width=120 if col != "name" else 250)
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def _build_status_bar(self):
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(status_frame, textvariable=self.status_var, anchor="w").pack(fill=tk.X)

    def connect_ssh(self):
        host = self.ssh_host_var.get().strip()
        if not host:
            messagebox.showerror("Error", "Please enter an SSH host alias.")
            return
        vm_device_path = self.vm_device_path_var.get() or "~/.local/bin/vm-device"
        self.client = SSHVMDeviceClient(host, vm_device_path=vm_device_path)
        self.status_var.set(f"Connected to {host}")
        # Sequential initial loading to avoid double sudo prompt
        threading.Thread(target=self._sequential_initial_load, daemon=True).start()

    def _sequential_initial_load(self):
        self._load_attached()
        self._load_available()

    def refresh_attached(self):
        if not self.client:
            return
        self.status_var.set("Refreshing attached devices...")
        threading.Thread(target=self._load_attached, daemon=True).start()

    def refresh_available(self):
        if not self.client:
            return
        self.status_var.set("Refreshing available devices...")
        threading.Thread(target=self._load_available, daemon=True).start()

    def _load_attached(self, retry=False):
        result = self.client.list_attached()
        sudo_error = self._is_sudo_error(result)
        if sudo_error and not retry:
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._load_attached(retry=True)
                return
        self._update_device_table(self.attached_tree, result, "attached_devices")

    def _load_available(self, retry=False):
        result = self.client.list_available()
        sudo_error = self._is_sudo_error(result)
        if sudo_error and not retry:
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._load_available(retry=True)
                return
        self._update_device_table(self.available_tree, result, "available_devices")

    def _update_device_table(self, tree, result, key):
        def update():
            tree.delete(*tree.get_children())
            if result.get("success", True) and key in result:
                for dev in result[key]:
                    tree.insert("", "end", values=(dev["vendor"], dev["product"], dev["name"], dev["status"]))
                self.status_var.set("Loaded devices.")
            else:
                self.status_var.set(result.get("error", "Failed to load devices."))
        self.after(0, update)
        # Always update tray menu after device table update
        if hasattr(self, "tray_manager"):
            self.after(100, self.tray_manager.update_menu)

    def _on_attached_select(self, event):
        selected = self.attached_tree.selection()
        self.detach_btn.config(state=tk.NORMAL if selected else tk.DISABLED)

    def _on_available_select(self, event):
        selected = self.available_tree.selection()
        self.attach_btn.config(state=tk.NORMAL if selected else tk.DISABLED)

    def detach_selected(self):
        selected = self.attached_tree.selection()
        if not selected:
            return
        values = self.attached_tree.item(selected[0], "values")
        vendor, product = values[0], values[1]
        self.status_var.set(f"Detaching {vendor}:{product}...")
        threading.Thread(target=self._detach_device, args=(vendor, product), daemon=True).start()

    def attach_selected(self):
        selected = self.available_tree.selection()
        if not selected:
            return
        values = self.available_tree.item(selected[0], "values")
        vendor, product = values[0], values[1]
        self.status_var.set(f"Attaching {vendor}:{product}...")
        threading.Thread(target=self._attach_device, args=(vendor, product), daemon=True).start()

    def _detach_device(self, vendor, product, retry=False):
        result = self.client.detach_device(vendor, product)
        if self._is_wrong_password(result):
            self.sudo_password = None
            self.client.set_sudo_password("")
            messagebox.showerror("Sudo Error", "Incorrect sudo password. Please try again.")
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._detach_device(vendor, product, retry=True)
                return
        sudo_error = self._is_sudo_error(result)
        if sudo_error and not retry:
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._detach_device(vendor, product, retry=True)
                return
        msg = result.get("error") or f"Detached {vendor}:{product}" if result.get("success") else "Failed to detach device."
        self.after(0, lambda: self.status_var.set(msg))
        self.refresh_attached()
        self.refresh_available()

    def _attach_device(self, vendor, product, retry=False):
        result = self.client.attach_device(vendor, product)
        if self._is_wrong_password(result):
            self.sudo_password = None
            self.client.set_sudo_password("")
            messagebox.showerror("Sudo Error", "Incorrect sudo password. Please try again.")
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._attach_device(vendor, product, retry=True)
                return
        sudo_error = self._is_sudo_error(result)
        if sudo_error and not retry:
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._attach_device(vendor, product, retry=True)
                return
        msg = result.get("error") or f"Attached {vendor}:{product}" if result.get("success") else "Failed to attach device."
        self.after(0, lambda: self.status_var.set(msg))
        self.refresh_attached()
        self.refresh_available()

    def _is_sudo_error(self, result):
        if not result or not result.get("error"):
            return False
        err = result["error"].lower()
        return (
            "sudo: a password is required" in err
            or "sudo: no tty present" in err
            or "sudo: unable to" in err
            or "is not in the sudoers file" in err
        )

    def _is_wrong_password(self, result):
        if not result or not result.get("error"):
            return False
        err = result["error"].lower()
        return (
            "sorry, try again." in err
            or "incorrect password" in err
            or "authentication failure" in err
        )

    def _on_close(self):
        print("Window close event triggered")
        self.withdraw()
        self.refresh_attached()
        self.refresh_available()
        self.after(1000, self.tray_manager.update_menu)
        self.tray_manager.start()

    def _on_minimize(self, event):
        print("Window minimize event triggered")
        if self.state() == "iconic":
            self.withdraw()
            self.refresh_attached()
            self.refresh_available()
            self.after(1000, self.tray_manager.update_menu)
            self.tray_manager.start()

    def get_attached_devices_for_tray(self):
        # Return a list of dicts: {name, vendor, product}
        items = []
        for row in self.attached_tree.get_children():
            values = self.attached_tree.item(row, "values")
            if values:
                items.append({"vendor": values[0], "product": values[1], "name": values[2]})
        return items

    def get_available_devices_for_tray(self):
        items = []
        for row in self.available_tree.get_children():
            values = self.available_tree.item(row, "values")
            if values:
                items.append({"vendor": values[0], "product": values[1], "name": values[2]})
        return items

    def tray_detach_device(self, vendor, product):
        threading.Thread(target=self._detach_device, args=(vendor, product), daemon=True).start()
        self.tray_manager.update_menu()

    def tray_reconnect_device(self, vendor, product):
        threading.Thread(target=self._reconnect_device, args=(vendor, product), daemon=True).start()
        self.tray_manager.update_menu()

    def tray_attach_device(self, vendor, product):
        threading.Thread(target=self._attach_device, args=(vendor, product), daemon=True).start()
        self.tray_manager.update_menu()

    def _reconnect_device(self, vendor, product, retry=False):
        result = self.client.reconnect_device(vendor, product)
        if self._is_wrong_password(result):
            self.sudo_password = None
            self.client.set_sudo_password("")
            messagebox.showerror("Sudo Error", "Incorrect sudo password. Please try again.")
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._reconnect_device(vendor, product, retry=True)
                return
        sudo_error = self._is_sudo_error(result)
        if sudo_error and not retry:
            pw = self.prompt_sudo_password()
            if pw:
                self.client.set_sudo_password(pw)
                self.sudo_password = pw
                self._reconnect_device(vendor, product, retry=True)
                return
        msg = result.get("error") or f"Reconnected {vendor}:{product}" if result.get("success") else "Failed to reconnect device."
        self.after(0, lambda: self.status_var.set(msg))
        self.refresh_attached()
        self.refresh_available()

if __name__ == "__main__":
    app = VMDeviceGUI()
    app.mainloop()