#!/bin/bash

echo "======================================"
echo "DisplayStation v1 Installer Starting"
echo "======================================"

# Make BASE_DIR wherever this script is located
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# -----------------------------
# 1️⃣ Install Dependencies
# -----------------------------
echo "[1/4] Installing dependencies..."

sudo apt update
sudo apt install -y \
ffmpeg \
yad \
python3 \
python3-pip \
python3-tk

echo "Dependencies installed."
echo ""

# -----------------------------
# 2️⃣ Make scripts executable
# -----------------------------
echo "[2/4] Setting permissions for scripts..."

find "$BASE_DIR" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;

echo "Scripts in $BASE_DIR are now executable."
echo ""

# -----------------------------
# 3️⃣ Create Desktop shortcut dynamically
# -----------------------------
echo "[3/4] Creating Desktop shortcut..."

DESKTOP_DIR="$HOME/Desktop"
DESKTOP_FILE="$DESKTOP_DIR/DisplayStation.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=DisplayStation
Comment=Launch DisplayStation Camera Viewer
Exec=$BASE_DIR/startDisplayLauncher.py
Icon=$BASE_DIR/icon.png
Terminal=false
Categories=Utility;Video;
EOF

chmod +x "$DESKTOP_FILE"
gio set "$DESKTOP_FILE" metadata::trusted true

echo "Desktop shortcut created."
echo ""

# -----------------------------
# 4️⃣ Setup auto-start properly
# -----------------------------
echo "[4/4] Configuring DisplayStation to run on boot..."

AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

BOOT_DESKTOP="$AUTOSTART_DIR/DisplayStationBoot.desktop"

cat > "$BOOT_DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Exec=bash -c "sleep 10 && $BASE_DIR/runOnBoot/startDisplayStationOnBoot.sh"
Icon=$BASE_DIR/icon.png
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=DisplayStation Boot
Comment=Start DisplayStation on login
EOF

chmod +x "$BOOT_DESKTOP"
gio set "$BOOT_DESKTOP" metadata::trusted true

echo "Autostart entry created."
echo ""

bash scripts/configureZorin.sh

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
