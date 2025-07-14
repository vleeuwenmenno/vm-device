import threading
import functools

try:
    import pystray
    from pystray import MenuItem as Item, Menu
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

class TrayManager:
    def __init__(self, gui):
        self.gui = gui
        self.icon = None
        self.tray_thread = None
        self._stop = threading.Event()

    def start(self):
        if not PYSTRAY_AVAILABLE:
            print("pystray or Pillow is not installed. System tray support is disabled.")
            return
        if self.icon is not None:
            print("Tray icon already running.")
            return
        print("Starting tray icon thread...")
        try:
            self.tray_thread = threading.Thread(target=self._run_tray, daemon=True)
            self.tray_thread.start()
        except Exception as e:
            print(f"Failed to start tray icon: {e}")

    def _run_tray(self):
        try:
            image = self._create_icon()
            self.icon = pystray.Icon("vm-device-gui", image, "VM Device GUI", self._build_menu())
            # Workaround: assign both click and double-click to show/hide for Windows reliability
            self.icon.on_click = self._on_double_click
            self.icon.on_double_click = self._on_double_click
            print("Tray icon started. Look for a blue USB icon in your system tray (may be hidden by Windows).")
            self.icon.run()
        except Exception as e:
            print(f"Tray icon failed to run: {e}")

    def _on_double_click(self, icon, event=None):
        self._toggle_main_window(icon, None)

    def _create_icon(self):
        # Simple blue USB icon
        img = Image.new("RGB", (64, 64), "white")
        d = ImageDraw.Draw(img)
        d.rectangle([20, 10, 44, 54], fill="blue", outline="black")
        d.rectangle([28, 54, 36, 62], fill="blue", outline="black")
        return img

    def _build_menu(self):
        # Fetch latest device lists from GUI
        attached = self.gui.get_attached_devices_for_tray()
        available = self.gui.get_available_devices_for_tray()

        attached_items = []
        for dev in attached:
            name = dev["name"]
            vendor = dev["vendor"]
            product = dev["product"]
            attached_items.append(
                Item(
                    f"{name} ({vendor}:{product})",
                    Menu(
                        Item("Detach", functools.partial(self._tray_detach, vendor, product)),
                        Item("Reconnect", functools.partial(self._tray_reconnect, vendor, product)),
                    ),
                )
            )

        available_items = []
        for dev in available:
            name = dev["name"]
            vendor = dev["vendor"]
            product = dev["product"]
            available_items.append(
                Item(
                    f"{name} ({vendor}:{product})",
                    Menu(
                        Item("Attach", functools.partial(self._tray_attach, vendor, product)),
                    ),
                )
            )

        menu = Menu(
            Item("Attached Devices", Menu(*attached_items)) if attached_items else Item("Attached Devices", None, enabled=False),
            Item("Available Devices", Menu(*available_items)) if available_items else Item("Available Devices", None, enabled=False),
            Menu.SEPARATOR,
            Item("Show/Hide Main Window", self._toggle_main_window),
            Item("Exit", self._exit_app),
        )
        return menu

    def _tray_detach(self, vendor, product, icon=None, item=None):
        self.gui.tray_detach_device(vendor, product)

    def _tray_reconnect(self, vendor, product, icon=None, item=None):
        self.gui.tray_reconnect_device(vendor, product)

    def _tray_attach(self, vendor, product, icon=None, item=None):
        self.gui.tray_attach_device(vendor, product)

    def _toggle_main_window(self, icon, item):
        if self.gui.state() == "withdrawn":
            self.gui.deiconify()
        else:
            self.gui.withdraw()

    def _exit_app(self, icon, item):
        self._stop.set()
        if self.icon:
            self.icon.stop()
        self.gui.quit()

    def update_menu(self):
        if self.icon:
            self.icon.menu = self._build_menu()