#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import os
import sys

class ChangeLayoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Layout")
        self.layout_changed = False

        # Window size
        self.root.geometry("400x300")

        # Instruction label
        tk.Label(self.root, text="Please select a layout file from the list below:").pack(pady=10)

        # Listbox for layout files
        self.layout_listbox = tk.Listbox(self.root, height=10, width=40)
        self.layout_listbox.pack(padx=10, pady=10)

        # Load layout files from 'customLayouts'
        self.layout_files = self.load_layout_files()
        if self.layout_files:
            for layout in self.layout_files:
                self.layout_listbox.insert(tk.END, layout)
        else:
            self.layout_listbox.insert(tk.END, "No layout files found.")

        # Select and Cancel buttons
        tk.Button(self.root, text="Select", command=self.select_layout).pack(pady=5)
        tk.Button(self.root, text="Cancel", command=self.cancel_and_exit).pack(pady=5)

    def load_layout_files(self):
        """Load all .txt layout files from customLayouts folder."""
        folder = "customLayouts"
        if not os.path.exists(folder):
            os.makedirs(folder)
            return []
        return [f for f in os.listdir(folder) if f.endswith(".txt")]

    def select_layout(self):
        """Handle selection and update SETTINGS.txt."""
        selection = self.layout_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a layout file.")
            return

        selected_layout = self.layout_listbox.get(selection[0])
        self.update_settings_file(selected_layout)
        self.layout_changed = True
        self.root.destroy()

    def update_settings_file(self, selected_layout):
        """Replace LAYOUT_FILE in SETTINGS.txt with selected layout."""
        settings_file = "SETTINGS.txt"
        try:
            lines = []
            if os.path.exists(settings_file):
                with open(settings_file, "r") as f:
                    lines = f.readlines()

            found = False
            for i, line in enumerate(lines):
                if line.strip().startswith("LAYOUT_FILE="):
                    lines[i] = f"LAYOUT_FILE={selected_layout}\n"
                    found = True
                    break

            if not found:
                # If no LAYOUT_FILE exists, add it at the top
                lines.insert(0, f"LAYOUT_FILE={selected_layout}\n")

            with open(settings_file, "w") as f:
                f.writelines(lines)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update SETTINGS.txt: {e}")

    def cancel_and_exit(self):
        self.layout_changed = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ChangeLayoutApp(root)
    root.mainloop()

    # Exit code: 1 if layout changed, 0 if canceled
    sys.exit(1 if app.layout_changed else 0)

if __name__ == "__main__":
    main()
