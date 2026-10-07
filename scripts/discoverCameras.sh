#!/usr/bin/env bash
set -e

OUT="$1"
SUBNET="${2:-}"

if [[ -z "$OUT" ]]; then
    echo "Usage: $0 /path/to/output.txt [subnet]"
    echo "Example: $0 onvifScan_10.1.24.0_24.txt 10.1.24.0/24"
    exit 1
fi

mkdir -p "$(dirname "$OUT")"
> "$OUT"

if [[ -n "$SUBNET" ]]; then
    echo "[*] Probing subnet $SUBNET (routed hosts only, no multicast)..."
    python3 - "$SUBNET" "$OUT" << 'PY'
import ipaddress
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

subnet, out_path = sys.argv[1], sys.argv[2]
try:
    network = ipaddress.ip_network(subnet, strict=False)
except ValueError as exc:
    sys.exit(f"Invalid subnet {subnet!r}: {exc}")

hosts = list(network.hosts())
if not hosts:
    hosts = [network.network_address]
if len(hosts) > 1024:
    sys.exit(f"Refusing to probe {len(hosts)} addresses. Use a /22 or smaller.")

# 554 is RTSP. The others are common camera/ONVIF web ports.
ports = (554, 80, 8000, 8080, 8899)

def probe(ip):
    ip = str(ip)
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.35)
        try:
            if sock.connect_ex((ip, port)) == 0:
                return ip, port
        except OSError:
            pass
        finally:
            sock.close()
    return None

found = []
with ThreadPoolExecutor(max_workers=64) as pool:
    futures = [pool.submit(probe, ip) for ip in hosts]
    for future in as_completed(futures):
        hit = future.result()
        if hit:
            found.append(hit)

found.sort(key=lambda item: ipaddress.ip_address(item[0]))
with open(out_path, "w") as handle:
    for ip, port in found:
        # MAC is not visible across a router. UNKNOWN keeps the 8-line camera format valid.
        xaddr = f"http://{ip}/onvif/device_service"
        handle.write(f"{ip} UNKNOWN {xaddr} 1\n")
        print(f"{ip} UNKNOWN {xaddr} 1  (port {port})")
print(f"[+] {len(found)} host(s) answered in {subnet}")
PY
    echo "[✓] Subnet discovery complete. Results saved to $OUT"
    exit 0
fi

echo "[*] Installing ONVIF discovery dependencies..."
python3 - << 'PY' || python3 -m pip install --user --break-system-packages wsdiscovery onvif-zeep
import wsdiscovery, onvif
PY

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
        m = re.match(r"http://(\d{1,3}(?:\.\d{1,3}){3})", xaddr)
        if m:
            ip = m.group(1)
            if ip in seen_ips:
                continue
            seen_ips.add(ip)

            subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            result = subprocess.run(["ip", "neigh", "show", ip],
                                    capture_output=True, text=True)
            mac = "UNKNOWN"
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    mac = parts[4]

            flag = 1 if xaddr.endswith("onvif/device_service") else 0
            print(f"{ip} {mac} {xaddr} {flag}")

wsd.stop()
EOF

echo "[✓] Discovery complete. Results saved to $OUT"
echo "[*] Printing discovery results:"
cat "$OUT"
