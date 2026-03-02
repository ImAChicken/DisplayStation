#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import subprocess
import os
import sys

# ==========================================
# Base Directory (Auto-detected)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

START_DISPLAY_SCRIPT = os.path.join(BASE_DIR, "DisplayStation.sh")
NEW_LAYOUT_SCRIPT = os.path.join(BASE_DIR, "createLayout1.py")
SET_LAYOUT_SCRIPT = os.path.join(BASE_DIR, "changeLayout.py")
CAMERA_MANAGER_SCRIPT = os.path.join(BASE_DIR, "rtsp1_camera_manager.py")
EDIT_SETTINGS_SCRIPT = os.path.join(BASE_DIR, "editSettings.py") 
RESTORE_DEFAULTS_SCRIPT = os.path.join(BASE_DIR, "restoreDefaults.py")

class DisplayLauncher(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("DisplayStation Launcher")
        self.geometry("350x300")  # slightly taller to fit new button
        self.resizable(False, False)

        icon_path = os.path.join(BASE_DIR, "icon_tk.png")
        try:
            if os.path.exists(icon_path):
                self._icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, self._icon)
        except Exception as e:
            print(f"[WARN] Failed to load icon: {e}")

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="DisplayStation",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 15))

        ttk.Button(
            frame,
            text="Start DisplayStation",
            command=self.start_displaystation
        ).pack(fill="x", pady=5)

        ttk.Button(
            frame,
            text="New Camera Layout",
            command=self.new_camera_layout
        ).pack(fill="x", pady=5)

        ttk.Button(
            frame,
            text="Set Camera Layout",
            command=self.set_camera_layout
        ).pack(fill="x", pady=5)

        ttk.Button(
            frame,
            text="Add / Remove Cameras",
            command=self.open_camera_manager
        ).pack(fill="x", pady=5)

        # =========================
        # New Button for Edit Settings
        # =========================
        ttk.Button(
            frame,
            text="Edit SETTINGS.txt",
            command=self.edit_settings
        ).pack(fill="x", pady=5)

        ttk.Button(
            frame,
            text="Restore Defaults",
            command=self.restore_defaults
        ).pack(fill="x", pady=5)

    # =========================
    # Launch Helpers
    # =========================

    def launch_script(self, command_list, description):
        script_path = command_list[-1]

        if not os.path.exists(script_path):
            print(f"[ERROR] {description} not found at: {script_path}")
            return

        try:
            subprocess.Popen(
                command_list,
                cwd=BASE_DIR,
                start_new_session=True
            )
            self.after(200, self.destroy)
        except Exception as e:
            print(f"[ERROR] Failed to launch {description}: {e}")

    # =========================
    # Button Methods
    # =========================

    def start_displaystation(self):
        print("Starting DisplayStation...")
        self.launch_script(
            [START_DISPLAY_SCRIPT],
            "DisplayStation.sh"
        )

    def new_camera_layout(self):
        print("Opening New Camera Layout...")
        self.launch_script(
            [sys.executable, NEW_LAYOUT_SCRIPT],
            "createLayout1.py"
        )

    def set_camera_layout(self):
        print("Opening Set Camera Layout...")
        self.launch_script(
            [sys.executable, SET_LAYOUT_SCRIPT],
            "changeLayout.py"
        )

    def open_camera_manager(self):
        print("Opening Camera Manager...")
        self.launch_script(
            [sys.executable, CAMERA_MANAGER_SCRIPT],
            "rtsp1_camera_manager.py"
        )

    def edit_settings(self):
        print("Opening Edit Settings...")
        self.launch_script(
            [sys.executable, EDIT_SETTINGS_SCRIPT],
            "editSettings.py"
        )

    def restore_defaults(self):
        print("Opening Restore Defaults...")
        self.launch_script(
            [sys.executable, RESTORE_DEFAULTS_SCRIPT],
            "restoreDefaults.py"
        )

    


if __name__ == "__main__":
    DisplayLauncher().mainloop()