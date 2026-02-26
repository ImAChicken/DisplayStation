#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import os

# ================================
# Edit Settings GUI for SETTINGS.txt
# ================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where script is located
SETTINGS_FILE = os.path.join(BASE_DIR, "SETTINGS.txt")

# Descriptions for each setting key
DESCRIPTIONS = {
    "LAYOUT_FILE": "Filename of the layout to load at startup (from customLayouts).",
    "DISPLAY_WIDTH": "Width of the display in pixels.",
    "DISPLAY_HEIGHT": "Height of the display in pixels.",
    "REBOOT_TIMER": "Time before automatic screen refresh (e.g., 2h).",
    "RUN_INDEFINITE": "1 = run indefinitely, 0 = test mode (camera loop runs 5 times).",
    "RESTART_TIME": "Daily restart time (HH:MM, 24h format)."
}

class SettingsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Edit SETTINGS.txt")
        self.root.geometry("600x400")

        self.settings = self.load_settings()
        self.entries = {}

        # Frame for the scrollable area
        canvas = tk.Canvas(root)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_ui()

    def load_settings(self):
        settings = {}
        if not os.path.exists(SETTINGS_FILE):
            messagebox.showerror("Error", f"SETTINGS.txt not found at {SETTINGS_FILE}")
            self.root.destroy()
            return {}

        with open(SETTINGS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                settings[key.strip()] = value.strip()
        return settings

    def build_ui(self):
        for i, (key, value) in enumerate(self.settings.items()):
            description = DESCRIPTIONS.get(key, "No description available.")

            # Label for the key
            ttk.Label(self.scrollable_frame, text=key, font=("Segoe UI", 10, "bold")).grid(row=i*2, column=0, sticky="w", padx=5, pady=2)
            # Label for description
            ttk.Label(self.scrollable_frame, text=description, font=("Segoe UI", 9), foreground="gray").grid(row=i*2+1, column=0, sticky="w", padx=5, pady=(0,5))
            # Entry for value
            entry = ttk.Entry(self.scrollable_frame, width=40)
            entry.insert(0, value)
            entry.grid(row=i*2, column=1, sticky="w", padx=5, pady=2)
            self.entries[key] = entry

        # Save button
        save_btn = ttk.Button(self.scrollable_frame, text="Save Settings", command=self.save_settings)
        save_btn.grid(row=len(self.settings)*2, column=0, columnspan=2, pady=15)

    def save_settings(self):
        try:
            lines = []
            with open(SETTINGS_FILE, "r") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("#") or not stripped or "=" not in stripped:
                        lines.append(line)
                        continue
                    key = stripped.split("=", 1)[0].strip()
                    if key in self.entries:
                        value = self.entries[key].get()
                        lines.append(f"{key}={value}\n")
                    else:
                        lines.append(line)

            with open(SETTINGS_FILE, "w") as f:
                f.writelines(lines)

            messagebox.showinfo("Success", "Settings saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

def main():
    root = tk.Tk()
    app = SettingsEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()