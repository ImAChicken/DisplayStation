#!/usr/bin/env bash
set -e

RTSP_FILE="$1"
ONVIF_FILE="$2"

if [[ -z "$RTSP_FILE" || -z "$ONVIF_FILE" ]]; then
    echo "Usage: $0 RTSP1.txt onvifScan.txt"
    exit 1
fi

TMP_FILE="$(mktemp)"

# --- Step 1: Read onvifScan.txt into associative arrays ---
declare -A mac_to_ip
declare -A ip_to_mac

while read -r line; do
    [[ -z "$line" ]] && continue
    ip=$(echo "$line" | awk '{print $1}')
    mac=$(echo "$line" | awk '{print $2}')
    # Only IPv4
    if [[ "$ip" == *:* ]]; then
        continue
    fi
    # Only add if MAC is non-empty
    if [[ -n "$mac" ]]; then
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

        # --- Step 2a: Update IP if MAC exists and IP changed ---
        if [[ -n "$mac" && -n "${mac_to_ip[$mac]}" ]]; then
            new_ip="${mac_to_ip[$mac]}"
            if [[ "$ip" != "$new_ip" ]]; then
                echo "[*] Updating IP for $name ($mac) $ip → $new_ip"
                ip="$new_ip"
                block[2]="$ip"
            fi
        fi

        # --- Step 2b: Check for replaced cameras (IP matches, MAC mismatch) ---
        if [[ -n "$ip" && -n "${ip_to_mac[$ip]}" ]]; then
            expected_mac="${ip_to_mac[$ip]}"
            if [[ "$mac" != "$expected_mac" ]]; then
                echo "[*] Detected replaced camera at IP $ip ($mac → $expected_mac)"
                mac="$expected_mac"
                block[3]="$mac"
            fi
        fi

        # --- Step 2c: Fill missing MAC if IP exists in onvifScan ---
        if [[ -z "$mac" && -n "$ip" && -n "${ip_to_mac[$ip]}" ]]; then
            mac="${ip_to_mac[$ip]}"
            echo "[*] Filling missing MAC for $name at IP $ip → $mac"
            block[3]="$mac"
        fi

        # Write updated block to temp file
        for i in "${block[@]}"; do
            echo "$i"
        done >> "$TMP_FILE"

        # Reset block for next camera
        block=()
    fi
done < "$RTSP_FILE"

# Replace original file
mv "$TMP_FILE" "$RTSP_FILE"
echo "[✓] RTSP1.txt updated from onvifScan.txt"

