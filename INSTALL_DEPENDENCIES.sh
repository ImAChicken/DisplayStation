#!/bin/bash
# DisplayStation dependency installer
# Zorin 18 / Ubuntu 24.04 blocks system pip (PEP 668). Install the ONVIF
# packages with the override, then patch discoverCameras.sh so launch does
# not die on "externally-managed-environment".

echo "======================================"
echo "DisplayStation v1 Installer Starting"
echo "======================================"

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# -----------------------------
# 1. Install apt dependencies
# -----------------------------
echo "[1/5] Installing apt dependencies..."

sudo dpkg --configure -a
sudo apt update
sudo apt install -y \
  ffmpeg \
  yad \
  python3 \
  python3-pip \
  python3-tk \
  python3-venv \
  python3-lxml

echo "Apt dependencies installed."
echo ""

# -----------------------------
# 2. Python packages (PEP 668)
# -----------------------------
echo "[2/5] Installing Python ONVIF packages..."

python3 -m pip install --user --break-system-packages wsdiscovery onvif-zeep

echo "Python packages installed."
echo ""

# -----------------------------
# 3. Make scripts executable and stop the boot-time pip failure
# -----------------------------
echo "[3/5] Setting permissions and patching camera discovery..."

find "$BASE_DIR" -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;

DISCOVER="$BASE_DIR/scripts/discoverCameras.sh"
if [ -f "$DISCOVER" ]; then
  python3 - "$DISCOVER" << 'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
text = path.read_text()
old = "python3 -m pip install --user --quiet wsdiscovery onvif-zeep"
new = "python3 -m pip install --user --break-system-packages --quiet wsdiscovery onvif-zeep"
if old in text:
    path.write_text(text.replace(old, new, 1))
    print(f"Patched {path}")
elif new in text:
    print(f"Already patched: {path}")
else:
    print(f"WARNING: pip line not found in {path}. Discovery may still fail.")
PY
else
  echo "WARNING: $DISCOVER not found. Skipping patch."
fi

echo "Scripts in $BASE_DIR are now executable."
echo ""

# -----------------------------
# 4. Desktop shortcut
# -----------------------------
echo "[4/5] Creating Desktop shortcut..."

DESKTOP_DIR="$HOME/Desktop"
DESKTOP_FILE="$DESKTOP_DIR/DisplayStation.desktop"
mkdir -p "$DESKTOP_DIR"

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
gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true

echo "Desktop shortcut created."
echo ""

# -----------------------------
# 5. Autostart
# -----------------------------
echo "[5/5] Configuring DisplayStation to run on login..."

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
gio set "$BOOT_DESKTOP" metadata::trusted true 2>/dev/null || true

echo "Autostart entry created."
echo ""

if [ -f "$BASE_DIR/scripts/configureZorin.sh" ]; then
  bash "$BASE_DIR/scripts/configureZorin.sh"
fi

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
