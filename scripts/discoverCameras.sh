#!/usr/bin/env bash
set -e

OUT="$1"
if [[ -z "$OUT" ]]; then
    echo "Usage: $0 /path/to/output.txt"
    exit 1
fi

mkdir -p "$(dirname "$OUT")"
> "$OUT"

echo "[*] Installing ONVIF discovery dependencies..."
python3 -m pip install --user --quiet wsdiscovery onvif-zeep

echo "[*] Discovering ONVIF devices (IPv4 only)..."

python3 - << "EOF" | sort -rk4,4 -t' ' > "$OUT"
from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
import subprocess
import re

wsd = WSDiscovery()
wsd.start()

services = wsd.searchServices(timeout=5)
seen_ips = set()

for service in services:
    for xaddr in service.getXAddrs():
        # Only IPv4
        m = re.match(r"http://(\d{1,3}(?:\.\d{1,3}){3})", xaddr)
        if m:
            ip = m.group(1)
            if ip in seen_ips:
                continue
            seen_ips.add(ip)

            # Ping once to populate ARP table
            subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Get MAC
            result = subprocess.run(["ip", "neigh", "show", ip],
                                    capture_output=True, text=True)
            mac = "UNKNOWN"
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    mac = parts[4]

            # Check if XADDR ends with onvif/device_service
            flag = 1 if xaddr.endswith("onvif/device_service") else 0

            print(f"{ip} {mac} {xaddr} {flag}")

wsd.stop()
EOF

echo "[✓] Discovery complete. Results saved to $OUT"
echo "[*] Printing discovery results:"
cat "$OUT"

