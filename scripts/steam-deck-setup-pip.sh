#!/bin/bash
set -e
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user --break-system-packages
{ echo 'if [ -d "$HOME/.local/bin" ]; then'; echo ' PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc; echo 'fi' >> ~/.bashrc; } >> ~/.bashrc
