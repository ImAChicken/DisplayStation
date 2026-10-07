#!/usr/bin/env bash
set -e

RTSP_FILE="$1"
ONVIF_FILE="$2"

if [[ -z "$RTSP_FILE" || -z "$ONVIF_FILE" ]]; then
    echo "Usage: $0 RTSP1.txt onvifScan.txt"
    exit 1
fi

TMP_FILE="$(mktemp)"

is_real_mac() {
    local value="${1^^}"
    [[ -n "$value" && "$value" != "UNKNOWN" && "$value" =~ ^([0-9A-F]{2}:){5}[0-9A-F]{2}$ ]]
}

# --- Step 1: Read onvifScan.txt. Ignore UNKNOWN so it cannot replace a saved MAC. ---
declare -A mac_to_ip
declare -A ip_to_mac

while read -r line; do
    [[ -z "$line" ]] && continue
    ip=$(echo "$line" | awk '{print $1}')
    mac=$(echo "$line" | awk '{print $2}')
    if [[ "$ip" == *:* ]]; then
        continue
    fi
    if is_real_mac "$mac"; then
        mac_to_ip["$mac"]="$ip"
        ip_to_mac["$ip"]="$mac"
    fi
done < "$ONVIF_FILE"

# --- Step 2: Process RTSP1.txt in 8-line blocks ---
block=()
while IFS= read -r line || [[ -n "$line" ]]; do
    block+=("$line")
    if (( ${#block[@]} == 8 )); then
        index="${block[0]}"
        name="${block[1]}"
        ip="${block[2]}"
        mac="${block[3]}"

        # Update IP only when the saved MAC is real and the scan saw that same MAC.
        if is_real_mac "$mac" && [[ -n "${mac_to_ip[$mac]}" ]]; then
            new_ip="${mac_to_ip[$mac]}"
            if [[ "$ip" != "$new_ip" ]]; then
                echo "[*] Updating IP for $name ($mac) $ip → $new_ip"
                ip="$new_ip"
                block[2]="$ip"
            fi
        fi

        # Fill a missing MAC only. Never replace a real saved MAC.
        if ! is_real_mac "$mac" && [[ -n "$ip" && -n "${ip_to_mac[$ip]}" ]]; then
            mac="${ip_to_mac[$ip]}"
            echo "[*] Filling missing MAC for $name at IP $ip → $mac"
            block[3]="$mac"
        fi

        for i in "${block[@]}"; do
            echo "$i"
        done >> "$TMP_FILE"

        block=()
    fi
done < "$RTSP_FILE"

mv "$TMP_FILE" "$RTSP_FILE"
echo "[✓] RTSP1.txt updated from onvifScan.txt"
