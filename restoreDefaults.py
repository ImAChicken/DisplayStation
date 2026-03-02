#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil

# ==========================================
# Base Directory
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CUSTOM_LAYOUTS_DIR = os.path.join(BASE_DIR, "customLayouts")
RTSP_FILE = os.path.join(BASE_DIR, "RTSP1.txt")
SETTINGS_FILE = os.path.join(BASE_DIR, "SETTINGS.txt")


class RestoreDefaultsWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Restore Defaults")
        self.geometry("500x220")
        self.resizable(False, False)

        self.configure(padx=20, pady=20)

        self.build_ui()

    def build_ui(self):
        warning_label = ttk.Label(
            self,
            text="Are you sure you want to restore default settings?\n\n"
                 "Custom layouts will be destroyed and cameras must be re-added.",
            justify="center",
            font=("Segoe UI", 10)
        )
        warning_label.pack(pady=(0, 20))

        button_frame = ttk.Frame(self)
        button_frame.pack()

        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, padx=10)

        # Red DEFAULT button
        style = ttk.Style()
        style.configure(
            "Danger.TButton",
            foreground="white",
            background="red"
        )

        default_btn = tk.Button(   # use tk.Button for reliable red background
            button_frame,
            text="DEFAULT",
            bg="red",
            fg="white",
            activebackground="#aa0000",
            activeforeground="white",
            command=self.restore_defaults,
            width=12
        )
        default_btn.grid(row=0, column=1, padx=10)

    # ==========================================
    # Restore Logic
    # ==========================================
    def restore_defaults(self):
        try:
            # 1️⃣ Delete all files in customLayouts
            if os.path.exists(CUSTOM_LAYOUTS_DIR):
                for filename in os.listdir(CUSTOM_LAYOUTS_DIR):
                    file_path = os.path.join(CUSTOM_LAYOUTS_DIR, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)

            # 2️⃣ Blank RTSP1.txt
            if os.path.exists(RTSP_FILE):
                with open(RTSP_FILE, "w") as f:
                    f.write("")

            # 3️⃣ Set LAYOUT_FILE=null in SETTINGS.txt
            if os.path.exists(SETTINGS_FILE):
                lines = []
                with open(SETTINGS_FILE, "r") as f:
                    lines = f.readlines()

                updated_lines = []
                found = False

                for line in lines:
                    if line.strip().startswith("LAYOUT_FILE="):
                        updated_lines.append("LAYOUT_FILE=null\n")
                        found = True
                    else:
                        updated_lines.append(line)

                # If setting not present, add it
                if not found:
                    updated_lines.append("LAYOUT_FILE=null\n")

                with open(SETTINGS_FILE, "w") as f:
                    f.writelines(updated_lines)

            messagebox.showinfo("Success", "DisplayStation restored to defaults.")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore defaults:\n{e}")


if __name__ == "__main__":
    RestoreDefaultsWindow().mainloop()
