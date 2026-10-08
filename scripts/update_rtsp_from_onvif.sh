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

# --- Step 1: Local scan. UNKNOWN is ignored so it cannot replace a saved MAC. ---
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

# --- Step 2: Cameras the local scan saw. Move the IP, then check that new IP. ---
block=()
while IFS= read -r line || [[ -n "$line" ]]; do
    block+=("$line")
    if (( ${#block[@]} == 8 )); then
        name="${block[1]}"
        ip="${block[2]}"
        mac="${block[3]}"

        if is_real_mac "$mac" && [[ -n "${mac_to_ip[$mac]}" ]]; then
            new_ip="${mac_to_ip[$mac]}"
            if [[ "$ip" != "$new_ip" ]]; then
                echo "[*] Updating IP for $name ($mac) $ip → $new_ip"
                ip="$new_ip"
                block[2]="$ip"
            fi
            if [[ -n "${ip_to_mac[$ip]}" && "${ip_to_mac[$ip],,}" != "${mac,,}" ]]; then
                echo "[*] Detected replaced camera at IP $ip ($mac → ${ip_to_mac[$ip]})"
                mac="${ip_to_mac[$ip]}"
                block[3]="$mac"
            fi
        elif ! is_real_mac "$mac" && [[ -n "$ip" && -n "${ip_to_mac[$ip]}" ]]; then
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

# --- Step 3: Cameras the local scan did not see. Match the saved MAC on subnet scan hosts. ---
python3 - "$RTSP_FILE" "$ONVIF_FILE" << 'PY'
import pathlib
import re
import sys
import urllib.request
from urllib.request import HTTPDigestAuthHandler, HTTPPasswordMgrWithDefaultRealm, build_opener

rtsp_path = pathlib.Path(sys.argv[1])
local_scan = pathlib.Path(sys.argv[2])
mac_re = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")

def real(value):
    return bool(mac_re.fullmatch(value or "")) and value.upper() != "UNKNOWN"

def fetch_mac(ip, user, pwd):
    url = f"http://{ip}/ISAPI/System/Network/interfaces"
    password_mgr = HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, url, user, pwd)
    opener = build_opener(HTTPDigestAuthHandler(password_mgr))
    try:
        with opener.open(url, timeout=3) as response:
            body = response.read().decode("utf-8", "replace")
    except Exception:
        return ""
    match = mac_re.search(body)
    return match.group(0).lower() if match else ""

seen = set()
if local_scan.exists():
    for line in local_scan.read_text().splitlines():
        parts = line.split()
        if len(parts) > 1 and real(parts[1]):
            seen.add(parts[1].lower())

candidates = []
for scan in sorted(pathlib.Path(".").glob("onvifScan_*.txt")):
    for line in scan.read_text().splitlines():
        parts = line.split()
        if parts and parts[0] not in candidates:
            candidates.append(parts[0])

lines = rtsp_path.read_text().splitlines()
blocks = [lines[i:i + 8] for i in range(0, len(lines), 8) if len(lines[i:i + 8]) == 8]
changed = False
for block in blocks:
    mac = block[3].strip()
    if not real(mac) or mac.lower() in seen:
        continue
    ip = block[2].strip()
    user, pwd, name = block[4].strip(), block[5].strip(), block[1].strip()
    found_ip = ""
    for candidate in [ip, *[item for item in candidates if item != ip]]:
        if fetch_mac(candidate, user, pwd).lower() == mac.lower():
            found_ip = candidate
            break
    if found_ip and found_ip != ip:
        print(f"[*] Subnet check moved {name} ({mac}) {ip} → {found_ip}")
        block[2] = found_ip
        changed = True
        continue
    if found_ip:
        continue
    current = fetch_mac(ip, user, pwd)
    if real(current) and current.lower() != mac.lower():
        print(f"[*] Subnet check replaced camera at {ip} ({mac} → {current})")
        block[3] = current
        changed = True

if changed:
    rtsp_path.write_text("\n".join(line for block in blocks for line in block) + "\n")
print("[✓] Remaining cameras checked")
PY

echo "[✓] RTSP1.txt updated from onvifScan.txt"
