#!/usr/bin/env python3
"""
Dell keyboard volume-dial daemon for macOS.

The dial's rotation is reported on the Consumer Control HID collection
(usage_page 0x0c, usage 0x01) as [report_id=0x01, delta], where delta is
a 7-bit signed relative value: 1..63 = clockwise ticks, 65..127 = counter-
clockwise ticks (value - 128 gives the signed count). macOS's own HID
translation misreads this field as "Mute" against the device's report
descriptor, so we bypass it and read the raw report directly.

Requires: pip3 install hidapi --break-system-packages
May require Input Monitoring permission for the process running this
(Terminal, or python3 itself) in System Settings > Privacy & Security.
"""
import hid
import subprocess
import time
import sys

VID = 0x413c
PID = 0x2010
CONSUMER_USAGE_PAGE = 0x0c
CONSUMER_USAGE = 0x01

# Tune these if needed:
STEP_PER_TICK = 3       # volume % change per unit of delta
MAX_ABS_DELTA = 20      # values above this are treated as a different
                         # kind of report (e.g. a button code like mute=226)
                         # and ignored, so we never fight the buttons.
INVERT = False           # flip if up/down feels backwards

def find_device_path():
    for d in hid.enumerate(VID, PID):
        if d.get("usage_page") == CONSUMER_USAGE_PAGE and d.get("usage") == CONSUMER_USAGE:
            return d["path"]
    return None

def get_volume():
    out = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True, text=True
    )
    try:
        return int(out.stdout.strip())
    except ValueError:
        return 50

def set_volume(vol):
    vol = max(0, min(100, vol))
    subprocess.run([
        "osascript", "-e",
        f"set volume output volume {vol}", "-e", "set volume output muted false"
    ])

def main():
    path = find_device_path()
    if not path:
        print("Dell consumer-control interface not found. Is the keyboard plugged in?")
        sys.exit(1)

    h = hid.device()
    h.open_path(path)
    h.set_nonblocking(True)
    print("Listening for dial rotation. Ctrl+C to stop.")

    current = get_volume()

    while True:
        data = h.read(64)
        if data and len(data) >= 2 and data[0] == 0x01:
            raw = data[1]
            if raw == 0:
                time.sleep(0.005)
                continue
            signed = raw if raw < 64 else raw - 128
            if abs(signed) > MAX_ABS_DELTA:
                # Not a dial tick (likely a button usage code) — ignore.
                time.sleep(0.005)
                continue
            if INVERT:
                signed = -signed
            current = max(0, min(100, current + signed * STEP_PER_TICK))
            set_volume(current)
            print(f"delta={signed:+d}  volume={current}")
        time.sleep(0.005)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
