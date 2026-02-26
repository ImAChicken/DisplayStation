import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser

# -------------------------------
# File paths and commands
# -------------------------------
RTSP1_FILE = "RTSP1.txt"
ONVIF_FILE = "onvifScan.txt"

DISCOVER_CMD = ["bash", "scripts/discoverCameras.sh", ONVIF_FILE]
UPDATE_CMD = ["bash", "scripts/update_rtsp_from_onvif.sh", RTSP1_FILE, ONVIF_FILE]
 
# -------------------------------
# Network scan functions
# -------------------------------
def run_network_scan():
    """Runs the discoverCameras.sh and update_rtsp_from_onvif.sh scripts"""
    try:
        subprocess.run(DISCOVER_CMD, check=True)
        subprocess.run(UPDATE_CMD, check=True)
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Scan Failed", f"Network scan failed.\n\n{e}")
        return False

# -------------------------------
# Load RTSP1 cameras
# -------------------------------
def load_rtsp1():
    """Loads cameras from RTSP1.txt into a list of dicts without shifting lines."""
    cameras = []
    try:
        with open(RTSP1_FILE, "r") as f:
            lines = [line.rstrip("\n") for line in f]

        for i in range(0, len(lines), 8):
            block = lines[i:i+8]
            if len(block) < 8:
                block += [""] * (8 - len(block))  # pad incomplete blocks

            idx_line = block[0].strip()
            if not idx_line.isdigit():
                # skip empty or corrupted blocks
                continue
            idx = int(idx_line)

            cameras.append({
                "index": idx,
                "name": block[1],
                "ip": block[2],
                "mac": block[3],
                "user": block[4],
                "pwd": block[5],
                "main": block[6],
                "sub": block[7],
            })

    except FileNotFoundError:
        pass

    cameras.sort(key=lambda c: c["index"])
    return cameras


# -------------------------------
# Load ONVIF scan results
# -------------------------------
def load_onvif():
    """Loads cameras from onvifScan.txt into a dictionary keyed by (IP, MAC)"""
    cams = {}
    try:
        with open(ONVIF_FILE, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 4:
                    continue
                ip, mac, xaddr, status = parts
                cams[(ip, mac)] = {"xaddr": xaddr, "status": status}
    except FileNotFoundError:
        pass
    return cams

# -------------------------------
# Main Application Class
# -------------------------------
class CameraManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Camera Manager - Add or Edit Cameras")
        self.geometry("1750x820")

        # Initial network scan
        if not run_network_scan():
            return

        # Build UI and populate tables
        self.build_ui()
        self.refresh_tables()
        # Tag for already added cameras
        self.onvif_tree.tag_configure("added", background="#c8f7c5")

    # -------------------------------
    # Build the user interface
    # -------------------------------
    def build_ui(self):
        # -------------------------------
        # Current Cameras Table
        # -------------------------------
        self.rtsp_frame = ttk.LabelFrame(self, text="Current Cameras")
        self.rtsp_frame.pack(fill="both", expand=True, padx=10, pady=5)

        rtsp_cols = (
            "Index", "Name", "IP", "MAC",
            "Main RTSP Path", "Sub RTSP Path",
            "XADDR", "Status"
        )

        self.rtsp_tree = ttk.Treeview(self.rtsp_frame, columns=rtsp_cols, show="headings")
        for c in rtsp_cols:
            self.rtsp_tree.heading(c, text=c)
            self.rtsp_tree.column(c, width=215, anchor="w")
        self.rtsp_tree.pack(fill="both", expand=True)

        # Row coloring
        self.rtsp_tree.tag_configure("online", background="#c8f7c5")
        self.rtsp_tree.tag_configure("offline", background="#f7c5c5")  # Red for offline

        # Buttons below RTSP1 table
        rtsp_btns = ttk.Frame(self.rtsp_frame)
        rtsp_btns.pack(fill="x", pady=6)

        ttk.Button(rtsp_btns, text="Edit Selected Cam", command=self.edit_selected_cam).pack(side="left", padx=5)
        ttk.Button(rtsp_btns, text="Check Cam Password", command=self.check_cam_password).pack(side="left", padx=5)
        ttk.Button(rtsp_btns, text="Test Main RTSP", command=self.test_main_rtsp).pack(side="left", padx=5)
        ttk.Button(rtsp_btns, text="Test Sub RTSP", command=self.test_sub_rtsp).pack(side="left", padx=5)
        ttk.Button(rtsp_btns, text="Test Ping", command=self.test_ping).pack(side="left", padx=5)
        ttk.Button(rtsp_btns, text="Open HTTP", command=self.open_http_rtsp).pack(side="left", padx=5)
        ttk.Button(rtsp_btns, text="Delete Camera", command=self.delete_cam).pack(side="left", padx=5)

        # -------------------------------
        # ONVIF Scan Results Table
        # -------------------------------
        self.onvif_frame = ttk.LabelFrame(self, text="ONVIF Scan Results")
        self.onvif_frame.pack(fill="both", expand=True, padx=10, pady=5)

        onvif_cols = ("IP", "MAC", "XADDR", "Status")
        self.onvif_tree = ttk.Treeview(self.onvif_frame, columns=onvif_cols, show="headings")
        for c in onvif_cols:
            self.onvif_tree.heading(c, text=c)
            self.onvif_tree.column(c, width=340, anchor="w")
        self.onvif_tree.pack(fill="both", expand=True)

        self.onvif_tree.tag_configure("bad", background="#f7c5c5")  # Red for bad XADDR

        # Buttons below ONVIF table
        onvif_btns = ttk.Frame(self.onvif_frame)
        onvif_btns.pack(fill="x", pady=6)

        ttk.Button(onvif_btns, text="Add Selected Camera", command=self.add_selected_camera).pack(side="left", padx=5)
        ttk.Button(onvif_btns, text="Add Camera Manually", command=self.add_camera_manually).pack(side="left", padx=5)
        ttk.Button(onvif_btns, text="Test Ping", command=self.test_ping_onvif).pack(side="left", padx=5)
        ttk.Button(onvif_btns, text="Open HTTP", command=self.open_http_onvif).pack(side="left", padx=5)

        # Green scan button
        run_btn = tk.Button(
            onvif_btns,
            text="Run Network Scan",
            bg="#4CAF50",
            fg="white",
            font=("TkDefaultFont", 10, "bold"),
            command=self.run_network_scan_button
        )
        run_btn.pack(side="right", padx=10)

    # -------------------------------
    # Populate the tables
    # -------------------------------
    def refresh_tables(self):
        # Clear all rows
        for tree in (self.rtsp_tree, self.onvif_tree):
            for row in tree.get_children():
                tree.delete(row)

        self.rtsp_cameras = load_rtsp1()
        self.onvif_cameras = load_onvif()

        # Populate Current Cameras table
        for cam in self.rtsp_cameras:
            key = (cam["ip"], cam["mac"])
            onvif = self.onvif_cameras.get(key)

            if onvif:
                tag = "online"
                status = "Good"
                xaddr = onvif["xaddr"]
            else:
                tag = "offline"
                status = "Cam not detected - may need to test connection"
                xaddr = ""

            self.rtsp_tree.insert(
                "",
                "end",
                values=(
                    cam["index"], cam["name"], cam["ip"], cam["mac"],
                    cam["main"], cam["sub"], xaddr, status
                ),
                tags=(tag,)
            )

        # -------------------------------
        # Populate ONVIF table with already added cameras at the bottom
        # -------------------------------
        existing_rtsp = {(c["ip"], c["mac"]) for c in self.rtsp_cameras}
        new_cams = []
        added_cams = []

        for (ip, mac), data in self.onvif_cameras.items():
            if (ip, mac) in existing_rtsp:
                added_cams.append((ip, mac, data))
            else:
                new_cams.append((ip, mac, data))

        # Insert NEW cameras first
        for ip, mac, data in new_cams:
            tag = "bad" if data["status"] == "0" else ""
            status = "Bad XADDR URL - may not be a valid camera" if data["status"] == "0" else "Valid XADDR URL"
            self.onvif_tree.insert("", "end", values=(ip, mac, data["xaddr"], status), tags=(tag,))

        # Insert ALREADY-ADDED cameras last with green background
        for ip, mac, data in added_cams:
            self.onvif_tree.insert("", "end", values=(ip, mac, data["xaddr"], "Already Added"), tags=("added",))

    # -------------------------------
    # RTSP button methods (with debug prints)
    # -------------------------------
    def get_selected_rtsp_index(self):
        selected = self.rtsp_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a camera first")
            return None
        values = self.rtsp_tree.item(selected[0], "values")
        idx = int(values[0])
        print(f"[DEBUG] Selected RTSP camera index: {idx}")
        return idx

    def edit_selected_cam(self):
        idx = self.get_selected_rtsp_index()
        if idx is None:
            return

        # Find camera in RTSP list
        cam = next((c for c in self.rtsp_cameras if c["index"] == idx), None)
        if not cam:
            messagebox.showerror("Error", "Camera not found")
            return

        win = tk.Toplevel(self)
        win.title(f"Edit Camera - Index {idx}")
        win.geometry("520x480")  # a little taller to fit the note
        win.resizable(False, False)

        # -----------------------------
        # Add informational note at top
        # -----------------------------
        note_text = ("IP will auto update to match the MAC address so change may not be reflected "
                    "if the MAC is not also updated. If no MAC is added, the MAC will be collected from the IP.")
        note_label = tk.Label(win, text=note_text, wraplength=500, justify="left", fg="red")
        note_label.pack(padx=10, pady=(10, 0))  # top padding


        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="Camera Info")

        # Display Index as static label
        ttk.Label(info_tab, text="Index").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(info_tab, text=str(idx), foreground="gray").grid(row=0, column=1, sticky="w", pady=5)

        # Editable fields
        labels = ["Camera Name", "IP Address", "MAC Address", "Username", "Password"]
        entries = []
        values = [cam["name"], cam["ip"], cam["mac"], cam["user"], cam["pwd"]]

        for i, (label, val) in enumerate(zip(labels, values), start=1):
            ttk.Label(info_tab, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entry = ttk.Entry(info_tab, width=30)
            entry.grid(row=i, column=1, pady=5)
            entry.insert(0, val)
            entries.append(entry)

        # Password masking
        entries[4].config(show="*")

        # Streams Tab
        stream_tab = ttk.Frame(notebook)
        notebook.add(stream_tab, text="Streams")

        single_stream = tk.BooleanVar(value=False)

        ttk.Label(stream_tab, text="Main Stream Path").grid(row=0, column=0, sticky="w", pady=5)
        main_entry = ttk.Entry(stream_tab, width=40)
        main_entry.grid(row=0, column=1, pady=5)
        main_entry.insert(0, cam["main"])

        ttk.Label(stream_tab, text="Sub Stream Path").grid(row=1, column=0, sticky="w", pady=5)
        sub_entry = ttk.Entry(stream_tab, width=40)
        sub_entry.grid(row=1, column=1, pady=5)
        sub_entry.insert(0, cam["sub"])

        ttk.Checkbutton(stream_tab, text="Single Stream (use Main for both)", variable=single_stream).grid(row=2, column=1, sticky="w", pady=5)

        # ----------------------------
        # Button Commands
        # ----------------------------
        def save_camera():
            new_name = entries[0].get().strip()
            new_ip = entries[1].get().strip()
            new_mac = entries[2].get().strip()
            new_user = entries[3].get().strip()
            new_pwd = entries[4].get().strip()
            new_main = main_entry.get().strip()
            new_sub = main_entry.get().strip() if single_stream.get() else sub_entry.get().strip()

            if not new_ip or not new_name:
                messagebox.showerror("Missing Info", "IP Address and Camera Name are required")
                return

            # Load file
            try:
                with open(RTSP1_FILE, "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                messagebox.showerror("Error", "RTSP1.txt not found")
                return

            # Ensure multiples of 8
            if len(lines) % 8 != 0:
                lines += ["\n"] * (8 - len(lines) % 8)

            # Find block for this index
            for i in range(0, len(lines), 8):
                if lines[i].strip() == str(idx):
                    lines[i:i+8] = [
                        f"{idx}\n",
                        f"{new_name}\n",
                        f"{new_ip}\n",
                        f"{new_mac}\n",
                        f"{new_user}\n",
                        f"{new_pwd}\n",
                        f"{new_main}\n",
                        f"{new_sub}\n"
                    ]
                    break

            # Write back
            with open(RTSP1_FILE, "w") as f:
                f.writelines(lines)

            self.refresh_tables()
            win.destroy()

        def test_ping():
            ip_val = entries[1].get().strip()
            if not ip_val:
                messagebox.showerror("Missing Info", "IP Address is required")
                return
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ping {ip_val}"])

        def test_main_stream():
            ip_val = entries[1].get().strip()
            user_val = entries[3].get().strip()
            pwd_val = entries[4].get().strip()
            main = main_entry.get().strip()
            if not ip_val or not user_val or not pwd_val:
                messagebox.showerror("Missing Info", "IP, Username, and Password are required")
                return
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ffplay -rtsp_transport tcp rtsp://{user_val}:{pwd_val}@{ip_val}{main}"])

        def test_sub_stream():
            ip_val = entries[1].get().strip()
            user_val = entries[3].get().strip()
            pwd_val = entries[4].get().strip()
            sub = main_entry.get().strip() if single_stream.get() else sub_entry.get().strip()
            if not ip_val or not user_val or not pwd_val:
                messagebox.showerror("Missing Info", "IP, Username, and Password are required")
                return
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ffplay -rtsp_transport tcp rtsp://{user_val}:{pwd_val}@{ip_val}{sub}"])

        # ----------------------------
        # Bottom Buttons
        # ----------------------------
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Save", command=save_camera).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Test Ping", command=test_ping).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Test Main Stream", command=test_main_stream).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Test Sub Stream", command=test_sub_stream).pack(side="left", padx=5)

    def check_cam_password(self):
        idx = self.get_selected_rtsp_index()
        if idx is None:
            return

        cam = next((c for c in self.rtsp_cameras if c["index"] == idx), None)
        if not cam:
            messagebox.showerror("Error", "Camera not found")
            return

        user = cam["user"]
        pwd = cam["pwd"]
        print(f"[DEBUG] Check Cam Password called for index: {idx}, Username: {user}, Password: {pwd}")

        messagebox.showinfo(
            f"Camera {cam['name']} Credentials",
            f"Username: {user}\nPassword: {pwd}"
        )

    # -------------------------------
    # Test Main RTSP for selected camera
    # -------------------------------
    def test_main_rtsp(self):
        idx = self.get_selected_rtsp_index()
        if idx is None:
            return

        cam = next((c for c in self.rtsp_cameras if c["index"] == idx), None)
        if not cam:
            messagebox.showerror("Error", "Selected camera not found")
            return

        if not cam["ip"] or not cam["user"] or not cam["pwd"] or not cam["main"]:
            messagebox.showerror("Missing Info", "IP, Username, Password, and Main Stream Path are required")
            return

        main_url = f"rtsp://{cam['user']}:{cam['pwd']}@{cam['ip']}{cam['main']}"
        print(f"[DEBUG] Test Main RTSP called for camera {cam['name']}, URL: {main_url}")
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ffplay -rtsp_transport tcp {main_url}"])


    # -------------------------------
    # Test Sub RTSP for selected camera
    # -------------------------------
    def test_sub_rtsp(self):
        idx = self.get_selected_rtsp_index()
        if idx is None:
            return

        cam = next((c for c in self.rtsp_cameras if c["index"] == idx), None)
        if not cam:
            messagebox.showerror("Error", "Selected camera not found")
            return

        if not cam["ip"] or not cam["user"] or not cam["pwd"] or not cam["sub"]:
            messagebox.showerror("Missing Info", "IP, Username, Password, and Sub Stream Path are required")
            return

        sub_url = f"rtsp://{cam['user']}:{cam['pwd']}@{cam['ip']}{cam['sub']}"
        print(f"[DEBUG] Test Sub RTSP called for camera {cam['name']}, URL: {sub_url}")
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ffplay -rtsp_transport tcp {sub_url}"])


    def test_ping(self):
        idx = self.get_selected_rtsp_index()
        if idx is not None:
            ip = next(c["ip"] for c in self.rtsp_cameras if c["index"] == idx)
            print(f"[DEBUG] Test Ping called for index: {idx}, IP: {ip}")
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ping {ip}"])

    def open_http_rtsp(self):
        idx = self.get_selected_rtsp_index()
        if idx is not None:
            ip = next(c["ip"] for c in self.rtsp_cameras if c["index"] == idx)
            print(f"[DEBUG] Open HTTP RTSP called for index: {idx}, IP: {ip}")
            webbrowser.open(f"http://{ip}")

    # -------------------------------
    # Delete Camera
    # -------------------------------
    def delete_cam(self):
        idx = self.get_selected_rtsp_index()
        if idx is None:
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete camera index {idx}?"):
            return

        try:
            with open(RTSP1_FILE, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            messagebox.showerror("Error", "RTSP1.txt not found")
            return

        for i in range(0, len(lines), 8):
            if lines[i].strip() == str(idx):
                # Blank out all lines except the index line
                lines[i+1:i+8] = ["\n"] * 7
                break

        with open(RTSP1_FILE, "w") as f:
            f.writelines(lines)

        self.refresh_tables()


    # -------------------------------
    # ONVIF button methods
    # -------------------------------
    def get_selected_onvif(self):
        selected = self.onvif_tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a camera first")
            return None
        values = self.onvif_tree.item(selected[0], "values")
        ip, mac = values[0], values[1]
        print(f"[DEBUG] Selected ONVIF camera IP={ip}, MAC={mac}")
        return ip, mac

    def add_selected_camera(self):
        sel = self.get_selected_onvif()
        if sel:
            ip, mac = sel
            print(f"[DEBUG] Add Selected Camera called with IP={ip}, MAC={mac}")
            self.open_add_camera_window(ip=ip, mac=mac)

    def add_camera_manually(self):
        print("[DEBUG] Add Camera Manually called")
        self.open_add_camera_window()

    def test_ping_onvif(self):
        sel = self.get_selected_onvif()
        if sel:
            ip, mac = sel
            print(f"[DEBUG] Test Ping ONVIF called for IP={ip}, MAC={mac}")
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ping {ip}"])

    def open_http_onvif(self):
        sel = self.get_selected_onvif()
        if sel:
            ip, mac = sel
            print(f"[DEBUG] Open HTTP ONVIF called for IP={ip}, MAC={mac}")
            webbrowser.open(f"http://{ip}")

    def run_network_scan_button(self):
        if run_network_scan():
            self.refresh_tables()

    # -------------------------------
    # Add Camera window logic (unchanged)
    # -------------------------------
    def open_add_camera_window(self, ip=None, mac=None):
        win = tk.Toplevel(self)
        win.title("Add Camera")
        win.geometry("520x440")
        win.resizable(False, False)

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="Camera Info")

        ttk.Label(info_tab, text="IP Address").grid(row=0, column=0, sticky="w", pady=5)
        ip_entry = ttk.Entry(info_tab, width=30)
        ip_entry.grid(row=0, column=1, pady=5)
        if ip:
            ip_entry.insert(0, ip)

        # Example IP format
        ttk.Label(info_tab, text="Example: 192.168.1.100", foreground="gray").grid(row=1, column=1, sticky="w", padx=2)

        ttk.Label(info_tab, text="MAC Address").grid(row=2, column=0, sticky="w", pady=5)
        mac_entry = ttk.Entry(info_tab, width=30)
        mac_entry.grid(row=2, column=1, pady=5)
        if mac:
            mac_entry.insert(0, mac)

        # Example MAC format
        ttk.Label(info_tab, text="Example: 00:1a:2b:3c:4d:5e", foreground="gray").grid(row=3, column=1, sticky="w", padx=2)


        ttk.Label(info_tab, text="Camera Name").grid(row=4, column=0, sticky="w", pady=5)
        name_entry = ttk.Entry(info_tab, width=30)
        name_entry.grid(row=4, column=1, pady=5)

        ttk.Label(info_tab, text="Username").grid(row=5, column=0, sticky="w", pady=5)
        user_entry = ttk.Entry(info_tab, width=30)
        user_entry.grid(row=5, column=1, pady=5)

        ttk.Label(info_tab, text="Password").grid(row=6, column=0, sticky="w", pady=5)
        pwd_entry = ttk.Entry(info_tab, width=30, show="*")
        pwd_entry.grid(row=6, column=1, pady=5)

        stream_tab = ttk.Frame(notebook)
        notebook.add(stream_tab, text="Streams")

        single_stream = tk.BooleanVar(value=False)

        ttk.Label(stream_tab, text="Main Stream Path").grid(row=0, column=0, sticky="w", pady=5)
        main_entry = ttk.Entry(stream_tab, width=40)
        main_entry.grid(row=0, column=1, pady=5)
        main_entry.insert(0, "/Streaming/Channels/101/1")

        ttk.Label(stream_tab, text="Sub Stream Path").grid(row=1, column=0, sticky="w", pady=5)
        sub_entry = ttk.Entry(stream_tab, width=40)
        sub_entry.grid(row=1, column=1, pady=5)
        sub_entry.insert(0, "/Streaming/Channels/101/2")

        ttk.Checkbutton(stream_tab, text="Single Stream (use Main for both)", variable=single_stream).grid(row=2, column=1, sticky="w", pady=5)

        ttk.Button(stream_tab, text="Test Stream").grid(row=3, column=1, sticky="e", pady=10)

        # Add camera logic
        def add_camera():
            ip_val = ip_entry.get().strip()
            mac_val = mac_entry.get().strip()
            name = name_entry.get().strip()
            user = user_entry.get().strip()
            pwd = pwd_entry.get().strip()
            main = main_entry.get().strip()
            sub = main if single_stream.get() else sub_entry.get().strip()

            if not ip_val or not name:
                messagebox.showerror("Missing Info", "IP Address and Camera Name are required")
                return

            # Load current file lines
            try:
                with open(RTSP1_FILE, "r") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []

            # Ensure total lines are multiple of 8
            if len(lines) % 8 != 0:
                lines += ["\n"] * (8 - len(lines) % 8)

            # Find first empty block
            block_index = None
            for i in range(0, len(lines), 8):
                if all(line.strip() == "" for line in lines[i+1:i+8]):
                    block_index = i
                    break

            if block_index is None:
                # No empty blocks, append at the end
                block_index = len(lines)
                lines += ["\n"] * 8

            # Use the first line of the block if it has a number, else assign next available
            existing_index_line = lines[block_index].strip()
            if existing_index_line.isdigit():
                cam_index = int(existing_index_line)
            else:
                # If no index, temporarily set 0 (we will repair indices later)
                cam_index = 0

            # Fill the block
            lines[block_index:block_index+8] = [
                f"{cam_index}\n",
                f"{name}\n",
                f"{ip_val}\n",
                f"{mac_val}\n",
                f"{user}\n",
                f"{pwd}\n",
                f"{main}\n",
                f"{sub}\n"
            ]

            # -----------------------
            # Repair all indices to start at 0 and be consecutive
            # -----------------------
            total_blocks = len(lines) // 8
            for b in range(total_blocks):
                lines[b*8] = f"{b}\n"

            # Write back to file
            with open(RTSP1_FILE, "w") as f:
                f.writelines(lines)

            self.refresh_tables()
            win.destroy()




        # ===============================
        # Bottom Buttons - inside open_add_camera_window
        # ===============================
        def test_main_stream():
            ip_val = ip_entry.get().strip()
            user_val = user_entry.get().strip()
            pwd_val = pwd_entry.get().strip()
            main = main_entry.get().strip()

            if not ip_val or not user_val or not pwd_val:
                messagebox.showerror("Missing Info", "IP Address, Username, and Password are required")
                return

            main_url = f"rtsp://{user_val}:{pwd_val}@{ip_val}{main}"
            print(f"Test Main Stream called for IP: {ip_val}, URL: {main_url}")
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ffplay -rtsp_transport tcp {main_url}"])

        def test_sub_stream():
            ip_val = ip_entry.get().strip()
            user_val = user_entry.get().strip()
            pwd_val = pwd_entry.get().strip()
            sub = sub_entry.get().strip() if not single_stream.get() else main_entry.get().strip()

            if not ip_val or not user_val or not pwd_val:
                messagebox.showerror("Missing Info", "IP Address, Username, and Password are required")
                return

            sub_url = f"rtsp://{user_val}:{pwd_val}@{ip_val}{sub}"
            print(f"Test Sub Stream called for IP: {ip_val}, URL: {sub_url}")
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"ffplay -rtsp_transport tcp {sub_url}"])


        def test_ping():
            ip_val = ip_entry.get().strip()
            if not ip_val:
                messagebox.showerror("Missing Info", "IP Address is required")
                return

            print(f"Test Ping called for IP: {ip_val}")
            subprocess.Popen([
                "gnome-terminal", "--",
                "bash", "-c",
                f"ping {ip_val}"
            ])
            print(f"New Terminal Window Opened for ping.")

        # Bottom frame buttons
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(stream_tab, text="Test Main Stream", command=test_main_stream).grid(row=3, column=0, sticky="w", pady=10)
        ttk.Button(stream_tab, text="Test Sub Stream", command=test_sub_stream).grid(row=3, column=1, sticky="e", pady=10)

        ttk.Button(btn_frame, text="Test Ping", command=test_ping).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Add Camera", command=add_camera).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="right")


# -------------------------------
# Run the application
# -------------------------------
if __name__ == "__main__":
    CameraManager().mainloop()
