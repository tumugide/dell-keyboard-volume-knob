#!/usr/bin/env python3
"""
Reads raw HID input reports from the Dell keyboard, bypassing macOS's
usage-name translation. Run this and rotate the dial to see the actual bytes.

Install first:
    pip3 install hidapi --break-system-packages

You may need to grant Terminal (or python3) Input Monitoring access:
System Settings > Privacy & Security > Input Monitoring
"""
import hid
import time

VID = 0x413c
PID = 0x2010

print("=== Matching HID interfaces ===")
infos = hid.enumerate(VID, PID)
for d in infos:
    print(f"  path={d['path']}  usage_page={hex(d.get('usage_page',0))}  "
          f"usage={hex(d.get('usage',0))}  interface={d.get('interface_number')}")

if not infos:
    print("No matching devices found. Check VID/PID or permissions.")
    raise SystemExit(1)

devices = []
for d in infos:
    try:
        h = hid.device()
        h.open_path(d['path'])
        h.set_nonblocking(True)
        devices.append((d, h))
        print(f"Opened: usage_page={hex(d.get('usage_page',0))} usage={hex(d.get('usage',0))}")
    except Exception as e:
        print(f"Could not open {d['path']}: {e}")

print("\n=== Reading raw reports. Rotate the dial (one direction, then the other). Ctrl+C to stop. ===\n")

try:
    while True:
        for d, h in devices:
            data = h.read(64)
            if data:
                print(f"[usage_page={hex(d.get('usage_page',0))} usage={hex(d.get('usage',0))}] "
                      f"{bytes(data).hex()}")
        time.sleep(0.005)
except KeyboardInterrupt:
    print("\nStopped.")
