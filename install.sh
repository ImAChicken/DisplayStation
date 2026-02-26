#!/bin/bash
# ====================================================
# DisplayStation One-Command Installer
# ====================================================

set -euo pipefail

# Define repo and target directory
REPO_URL="https://github.com/ImAChicken/DisplayStation.git"
TARGET_DIR="$HOME/DisplayStationv8"

echo "Starting DisplayStation installation..."
echo "Target directory: $TARGET_DIR"

# Check if target directory already exists
if [ -d "$TARGET_DIR" ]; then
    echo "Directory already exists. Pulling latest changes..."
    cd "$TARGET_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# Make sure INSTALL_DEPENDENCIES.sh is executable
chmod +x INSTALL_DEPENDENCIES.sh

echo "Running dependency installer..."
bash INSTALL_DEPENDENCIES.sh

echo "Installation complete! DisplayStation is ready."
echo "You can now run: bash $TARGET_DIR/DisplayStation.sh"
