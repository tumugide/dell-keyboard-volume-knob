#!/bin/bash
# Identifies the raw HID usage sent by the Dell keyboard's custom volume button on macOS.
# Run in Terminal. If output is empty, grant Terminal "Input Monitoring" permission
# in System Settings > Privacy & Security > Input Monitoring, then retry.

echo "=== HID devices matching 'Dell' ==="
hidutil list | grep -i dell
echo ""
echo "=== Monitoring all HID input ==="
echo "Press ONLY the volume/mute button 3-4 times now, then Ctrl+C."
echo "Avoid other keys/mouse movement so the log stays readable."
echo ""
hidutil monitor
