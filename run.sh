#!/bin/bash
# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Launch the GUI using the virtual environment python
# >/dev/null 2>&1 disassociates output to prevent hanging if launched via AppleScript
./venv/bin/python gui.py >/dev/null 2>&1 &
