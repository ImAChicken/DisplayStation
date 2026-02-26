#!/usr/bin/env python3

import tkinter as tk
import os
import signal

BUTTON_SIZE = 32     # smaller button
MARGIN = 4           # tight to corner

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)

screen_w = root.winfo_screenwidth()

pos_x = screen_w - BUTTON_SIZE - MARGIN
pos_y = MARGIN

root.geometry(f"{BUTTON_SIZE}x{BUTTON_SIZE}+{pos_x}+{pos_y}")

def close_program():
    os.system("pkill -f ffplay")      # kill all ffplay
    os.kill(os.getppid(), signal.SIGTERM)  # terminate parent shell script
    root.destroy()                   # terminate this overlay cleanly

btn = tk.Button(
    root,
    text="✕",
    font=("Arial", 14, "bold"),
    fg="white",
    bg="red",
    activebackground="dark red",
    borderwidth=0,
    highlightthickness=0,
    command=close_program
)

btn.pack(expand=True, fill="both")

root.mainloop()