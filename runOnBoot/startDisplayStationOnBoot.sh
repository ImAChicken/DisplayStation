#!/bin/bash
# ===============================================
# Boot Startup Script for DisplayStation
# Location: DisplayStationv8/runOnBoot/startDisplayStationOnBoot.sh
# ===============================================

# Base directory is the DisplayStationv8 folder (one level up from this script)
BASE_DIR="$(dirname "$(readlink -f "$0")")/.."
SETTINGS_FILE="$BASE_DIR/SETTINGS.txt"

# -----------------------------
# Load settings from SETTINGS.txt
# -----------------------------
if [ -f "$SETTINGS_FILE" ]; then
    source "$SETTINGS_FILE"
else
    echo "[WARN] SETTINGS.txt not found at $SETTINGS_FILE. Using default reboot time 20:00."
    RESTART_TIME="20:00"
fi

# -----------------------------
# Schedule system reboot
# -----------------------------
if [ -n "$RESTART_TIME" ]; then
    echo "Scheduling daily reboot at $RESTART_TIME..."
    shutdown -r "$RESTART_TIME"
else
    echo "[WARN] RESTART_TIME not set in SETTINGS.txt. Skipping reboot scheduling."
fi

# -----------------------------
# Start DisplayStation
# -----------------------------
echo "Starting DisplayStation..."
cd "$BASE_DIR" || exit 1
bash DisplayStation.sh
