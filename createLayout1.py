import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os

class CreateLayoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Create Layout")
        self.root.geometry("900x800")  # increased height for bigger grids

        self.camera_names = self.load_camera_names()
        self.dropdown_refs = []  # Store references to dropdowns for saving

        # Layout names and mapping
        self.layout_map = {
            "Single Screen": 1,
            "2x2 Grid": 2,
            "3x3 Grid": 3,
            "4x4 Grid": 4,
            "1 Big + 5 Small": 5,
            "2 Big + 8 Small": 6,
            "1 Big + 7 Small": 7,
            "1 Big + 12 Small": 8,
            "5x5 Grid": 9,
            "6x6 Grid": 10,
            "7x7 Grid": 11,
        }

        self.layout_names = list(self.layout_map.keys())
        self.layout_var = tk.StringVar(value="2x2 Grid")

        # Layout controls
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        import_button = tk.Button(control_frame, text="Import Layout", command=self.import_layout)
        import_button.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="Select Layout Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.layout_dropdown = ttk.Combobox(control_frame, textvariable=self.layout_var,
                                            values=self.layout_names, state="readonly")
        self.layout_dropdown.pack(side=tk.LEFT)
        self.layout_dropdown.bind("<<ComboboxSelected>>", self.update_layout_preview)

        save_button = tk.Button(control_frame, text="Save Layout", command=self.save_layout)
        save_button.pack(side=tk.LEFT, padx=10)

        # Preview frame
        self.preview_frame = tk.Frame(root)
        self.preview_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.update_layout_preview()

    # --------------------
    # Load camera names from RTSP1.txt
    # --------------------
    def load_camera_names(self):
        camera_names = []
        try:
            with open("RTSP1.txt", "r") as file:
                lines = [line.strip() for line in file if line.strip()]

            block = []
            for line in lines:
                block.append(line)
                if len(block) == 8:  # Each camera is 8 lines
                    index = int(block[0])
                    name = block[1]
                    camera_names.append((index, name))
                    block = []

        except FileNotFoundError:
            messagebox.showerror("File Error", "RTSP1.txt file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read RTSP1.txt: {e}")

        return camera_names

    # --------------------
    # Update layout preview
    # --------------------
    def update_layout_preview(self, event=None):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.dropdown_refs = []

        layout_type = self.layout_map.get(self.layout_var.get(), 2)

        if layout_type == 1:
            self.draw_grid(1, 1)
        elif layout_type == 2:
            self.draw_grid(2, 2)
        elif layout_type == 3:
            self.draw_grid(3, 3)
        elif layout_type == 4:
            self.draw_grid(4, 4)
        elif layout_type == 5:
            self.draw_custom_layout_5()
        elif layout_type == 6:
            self.draw_custom_layout_6()
        elif layout_type == 7:
            self.draw_custom_layout_7()
        elif layout_type == 8:
            self.draw_custom_layout_8()
        elif layout_type == 9:
            self.draw_grid(5, 5)
        elif layout_type == 10:
            self.draw_grid(6, 6)
        elif layout_type == 11:
            self.draw_grid(7, 7)

    # --------------------
    # Generic grid
    # --------------------
    def draw_grid(self, rows, cols):
        for r in range(rows):
            for c in range(cols):
                frame = tk.Frame(self.preview_frame, bd=1, relief=tk.RIDGE)
                frame.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                self.preview_frame.grid_rowconfigure(r, weight=1)
                self.preview_frame.grid_columnconfigure(c, weight=1)

                dropdown = ttk.Combobox(frame, values=[f"{i}: {name}" for i, name in self.camera_names])
                dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                self.dropdown_refs.append(dropdown)

    # --------------------
    # Custom layout 5 (existing)
    # --------------------
    def draw_custom_layout_5(self):
        positions = [[None]*3 for _ in range(3)]
        positions[0][0] = positions[0][1] = positions[1][0] = positions[1][1] = "BIG"
        small_positions = [(0,2), (1,2), (2,0), (2,1), (2,2)]

        for r in range(3):
            for c in range(3):
                if positions[r][c] == "BIG":
                    if r == 0 and c == 0:
                        frame = tk.Frame(self.preview_frame, bd=2, relief=tk.RIDGE, bg="gray")
                        frame.grid(row=r, column=c, rowspan=2, columnspan=2, sticky="nsew", padx=2, pady=2)
                        dropdown = ttk.Combobox(frame, values=[f"{i}: {name}" for i, name in self.camera_names])
                        dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                        self.dropdown_refs.append(dropdown)
                elif (r, c) in small_positions:
                    frame = tk.Frame(self.preview_frame, bd=1, relief=tk.RIDGE)
                    frame.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                    dropdown = ttk.Combobox(frame, values=[f"{i}: {name}" for i, name in self.camera_names])
                    dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                    self.dropdown_refs.append(dropdown)
                self.preview_frame.grid_rowconfigure(r, weight=1)
                self.preview_frame.grid_columnconfigure(c, weight=1)

    # --------------------
    # Custom layout 6 (existing)
    # --------------------
    def draw_custom_layout_6(self):
        for r in range(4):
            for c in range(4):
                if r == 0 and c in [0, 2]:
                    frame = tk.Frame(self.preview_frame, bd=2, relief=tk.RIDGE, bg="gray")
                    frame.grid(row=r, column=c, rowspan=2, columnspan=2, sticky="nsew", padx=2, pady=2)
                    dropdown = ttk.Combobox(frame, values=[f"{i}: {name}" for i, name in self.camera_names])
                    dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                    self.dropdown_refs.append(dropdown)
                elif r >= 2:
                    frame = tk.Frame(self.preview_frame, bd=1, relief=tk.RIDGE)
                    frame.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
                    dropdown = ttk.Combobox(frame, values=[f"{i}: {name}" for i, name in self.camera_names])
                    dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                    self.dropdown_refs.append(dropdown)
                self.preview_frame.grid_rowconfigure(r, weight=1)
                self.preview_frame.grid_columnconfigure(c, weight=1)

    # --------------------
    # New Layout 7 (1 Big + 7 Small, 4x4)
    # --------------------
    def draw_custom_layout_7(self):
        big_pos = (0,0)
        frame = tk.Frame(self.preview_frame, bd=2, relief=tk.RIDGE, bg="gray")
        frame.grid(row=big_pos[0], column=big_pos[1], rowspan=3, columnspan=3, sticky="nsew", padx=2, pady=2)
        dropdown = ttk.Combobox(frame, values=[f"{i}: {name}" for i, name in self.camera_names])
        dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.dropdown_refs.append(dropdown)

        # small screens
        small_positions = [(0,3),(1,3),(2,3),(3,0),(3,1),(3,2),(3,3)]
        for r,c in small_positions:
            f = tk.Frame(self.preview_frame, bd=1, relief=tk.RIDGE)
            f.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            dd = ttk.Combobox(f, values=[f"{i}: {name}" for i, name in self.camera_names])
            dd.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.dropdown_refs.append(dd)

        for i in range(4):
            self.preview_frame.grid_rowconfigure(i, weight=1)
            self.preview_frame.grid_columnconfigure(i, weight=1)

    # --------------------
    # New Layout 8 (1 Big + 12 Small, 4x4)
    # --------------------
    def draw_custom_layout_8(self):
        # Big screen in center 2x2
        big_positions = [(1,1)]
        frame = tk.Frame(self.preview_frame, bd=2, relief=tk.RIDGE, bg="gray")
        frame.grid(row=1, column=1, rowspan=2, columnspan=2, sticky="nsew", padx=2, pady=2)
        dropdown = ttk.Combobox(frame, values=[f"{i}: {name}" for i, name in self.camera_names])
        dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.dropdown_refs.append(dropdown)

        # small screens (12 surrounding)
        small_positions = [
            (0,0),(0,1),(0,2),(0,3),
            (1,0),(1,3),
            (2,0),(2,3),
            (3,0),(3,1),(3,2),(3,3)
        ]
        for r,c in small_positions:
            f = tk.Frame(self.preview_frame, bd=1, relief=tk.RIDGE)
            f.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            dd = ttk.Combobox(f, values=[f"{i}: {name}" for i, name in self.camera_names])
            dd.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.dropdown_refs.append(dd)

        for i in range(4):
            self.preview_frame.grid_rowconfigure(i, weight=1)
            self.preview_frame.grid_columnconfigure(i, weight=1)

    # --------------------
    # Save and import remain unchanged
    # --------------------
    def save_layout(self):
        layout_type_num = self.layout_map.get(self.layout_var.get(), 2)
        camera_indices = []
        unassigned = False

        for dropdown in self.dropdown_refs:
            value = dropdown.get()
            if value:
                try:
                    index = int(value.split(":")[0])
                    camera_indices.append(index)
                except (IndexError, ValueError):
                    camera_indices.append(-1)
                    unassigned = True
            else:
                camera_indices.append(-1)
                unassigned = True

        if unassigned:
            messagebox.showwarning("Unassigned Cameras", "Some screens are unassigned and will be saved as a blank screen.")

        # Prompt for layout name and replace spaces with underscores
        layout_name = simpledialog.askstring("Save Layout", "Enter layout name:")
        if layout_name is None:
            return  # User canceled
        layout_name = layout_name.strip().replace(" ", "_")  # Convert spaces to underscores
        if layout_name == "":
            messagebox.showerror("Invalid Name", "Layout name cannot be empty.")
            return

        os.makedirs("customLayouts", exist_ok=True)
        layout_file = f"customLayouts/{layout_name}.txt"

        if os.path.exists(layout_file):
            confirm = messagebox.askyesno("Overwrite?", f"A layout named '{layout_name}' already exists. Overwrite it?")
            if not confirm:
                return

        try:
            with open(layout_file, "w") as file:
                file.write(f"{layout_type_num}\n")
                for index in camera_indices:
                    file.write(f"{index}\n")
            messagebox.showinfo("Success", f"Layout '{layout_name}' saved successfully.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save layout: {e}")
            layout_type_num = self.layout_map.get(self.layout_var.get(), 2)
            camera_indices = []
            unassigned = False

            for dropdown in self.dropdown_refs:
                value = dropdown.get()
                if value:
                    try:
                        index = int(value.split(":")[0])
                        camera_indices.append(index)
                    except (IndexError, ValueError):
                        camera_indices.append(-1)
                        unassigned = True
                else:
                    camera_indices.append(-1)
                    unassigned = True

            if unassigned:
                messagebox.showwarning("Unassigned Cameras", "Some screens are unassigned and will be saved as a blank screen.")

            layout_name = simpledialog.askstring("Save Layout", "Enter layout name:")
            if not layout_name:
                return

            os.makedirs("customLayouts", exist_ok=True)
            layout_file = f"customLayouts/{layout_name}.txt"

            if os.path.exists(layout_file):
                confirm = messagebox.askyesno("Overwrite?", f"A layout named '{layout_name}' already exists. Overwrite it?")
                if not confirm:
                    return

            try:
                with open(layout_file, "w") as file:
                    file.write(f"{layout_type_num}\n")
                    for index in camera_indices:
                        file.write(f"{index}\n")
                messagebox.showinfo("Success", f"Layout '{layout_name}' saved successfully.")
                self.root.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save layout: {e}")

    def import_layout(self):
        layout_path = filedialog.askopenfilename(
            initialdir="customLayouts",
            title="Select layout file",
            filetypes=[("Text files", "*.txt")]
        )
        if not layout_path:
            return

        try:
            with open(layout_path, "r") as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

            layout_num = int(lines[0])
            reverse_map = {v: k for k, v in self.layout_map.items()}
            layout_name = reverse_map.get(layout_num, "2x2 Grid")
            self.layout_var.set(layout_name)
            self.update_layout_preview()

            for dropdown, value in zip(self.dropdown_refs, lines[1:]):
                idx = int(value)
                if idx >= 0 and idx < len(self.camera_names):
                    dropdown.set(f"{idx}: {self.camera_names[idx][1]}")
                else:
                    dropdown.set("")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import layout: {e}")


def main():
    root = tk.Tk()
    app = CreateLayoutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
