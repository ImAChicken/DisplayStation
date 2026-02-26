#!/bin/bash

echo "======================================"
echo "Configuring Zorin OS for DisplayStation Appliance"
echo "======================================"

# Prevent running entire script as root
if [ "$EUID" -eq 0 ]; then
    echo "Run this script as the normal user, NOT sudo."
    exit 1
fi

CURRENT_USER=$(whoami)

echo ""
echo "[1/6] Configuring Panel..."

gsettings set org.gnome.shell.extensions.zorin-taskbar intellihide true 2>/dev/null
gsettings set org.gnome.shell.extensions.zorin-taskbar intellihide-mode 'ALL_WINDOWS' 2>/dev/null

echo "Panel configured."
echo ""

echo "[2/6] Setting Super key behavior..."

gsettings set org.gnome.mutter overlay-key '' 2>/dev/null
gsettings set org.gnome.mutter overlay-key 'Super_L' 2>/dev/null

echo "Super key configured."
echo ""

echo "[3/6] Disabling screen blanking & sleep..."

gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing'
gsettings set org.gnome.desktop.screensaver lock-enabled false

echo "Sleep and lock disabled."
echo ""

echo "[4/6] Disabling ALL automatic updates..."

# Disable GUI update checks
gsettings set com.ubuntu.update-manager check-dist-upgrades 'never' 2>/dev/null
gsettings set com.ubuntu.update-manager regular-auto-launch-interval 0 2>/dev/null

# Disable backend APT periodic checks
sudo tee /etc/apt/apt.conf.d/10periodic > /dev/null <<EOF
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
APT::Periodic::Unattended-Upgrade "0";
EOF

# Disable unattended-upgrades service if present
if dpkg -l | grep -q unattended-upgrades; then
    sudo systemctl disable unattended-upgrades 2>/dev/null
    sudo systemctl stop unattended-upgrades 2>/dev/null
fi

echo "Automatic updates fully disabled."
echo ""

echo "[5/6] Enabling Auto Login..."

GDM_CONF="/etc/gdm3/custom.conf"

sudo sed -i "s/^#  AutomaticLoginEnable = true/AutomaticLoginEnable = true/" $GDM_CONF
sudo sed -i "s/^#  AutomaticLogin = .*/AutomaticLogin = $CURRENT_USER/" $GDM_CONF

# In case lines don't exist, ensure they are added
if ! grep -q "AutomaticLoginEnable" $GDM_CONF; then
    echo "AutomaticLoginEnable = true" | sudo tee -a $GDM_CONF > /dev/null
fi

if ! grep -q "AutomaticLogin =" $GDM_CONF; then
    echo "AutomaticLogin = $CURRENT_USER" | sudo tee -a $GDM_CONF > /dev/null
fi

echo "Auto login enabled for user: $CURRENT_USER"
echo ""

echo "[6/6] Finished."

echo ""
echo "======================================"
echo "Zorin appliance configuration complete."
echo "Reboot recommended."
echo "======================================"
