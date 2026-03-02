#!/bin/bash

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR" || exit 1

CONFIG_FILES=("SETTINGS.txt" "RTSP1.txt" "customLayouts")

# -------------------------------
# Verify git repo
# -------------------------------
if [ ! -d ".git" ]; then
    yad --error --title="Update Error" \
        --text="This is not a git repository.\nUpdates cannot be checked."
    exit 1
fi

# -------------------------------
# Fetch updates
# -------------------------------
git fetch

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    yad --info --title="Check for Updates" \
        --text="DisplayStation is already up to date."
    exit 0
fi

# -------------------------------
# Detect upstream config changes
# -------------------------------
CONFIG_CHANGED=0

for file in "${CONFIG_FILES[@]}"; do
    if git diff --name-only HEAD..@{u} | grep -q "^$file"; then
        CONFIG_CHANGED=1
        break
    fi
done

# -------------------------------
# Ask user if configs should be overwritten
# -------------------------------
OVERWRITE_CONFIG=1

if [ $CONFIG_CHANGED -eq 1 ]; then
    yad --question \
        --title="Configuration Files Changed" \
        --text="Updates include changes to configuration files.\n\nDo you want to OVERWRITE your local configuration?" \
        --button="Keep Local:1" \
        --button="Overwrite:0"

    OVERWRITE_CONFIG=$?
fi

# -------------------------------
# Backup local configs
# -------------------------------
BACKUP_DIR=".update_backup_$(date +%s)"
mkdir -p "$BACKUP_DIR"

for file in "${CONFIG_FILES[@]}"; do
    if [ -e "$file" ]; then
        cp -r "$file" "$BACKUP_DIR/" 2>/dev/null
    fi
done

# -------------------------------
# Pull updates
# -------------------------------
if ! git pull; then
    yad --error --title="Update Failed" \
        --text="Git pull failed.\nCheck your internet connection."
    rm -rf "$BACKUP_DIR"
    exit 1
fi

# -------------------------------
# Restore configs if user chose to keep them
# -------------------------------
if [ "$OVERWRITE_CONFIG" -ne 0 ]; then
    for file in "${CONFIG_FILES[@]}"; do
        if [ -e "$BACKUP_DIR/$file" ]; then
            rm -rf "$file"
            cp -r "$BACKUP_DIR/$file" .
        fi
    done

    yad --info --title="Update Complete" \
        --text="Update complete.\n\nLocal configuration files were preserved."
else
    yad --info --title="Update Complete" \
        --text="Update complete.\n\nConfiguration files were overwritten."
fi

rm -rf "$BACKUP_DIR"

exit 0
