#!/bin/bash
# Double-click me to start Khor Bros Menu Maker.
cd "$(dirname "$0")"

if [ ! -x ./KhorBrosMenu ]; then
    echo "Could not find KhorBrosMenu next to this launcher."
    echo "Make sure both files are in the same folder."
else
    ./KhorBrosMenu
fi

echo
echo "Press Enter to close this window..."
read _
