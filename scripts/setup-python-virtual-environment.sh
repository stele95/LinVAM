#!/bin/bash
set -e
echo "Setting up python virtual environment at ~/.local/share/LinVAM/venv"
mkdir -p ~/.local/share/LinVAM
python -m venv ~/.local/share/LinVAM/venv
source ~/.local/share/LinVAM/venv/bin/activate
python -m pip install --upgrade pip wheel
echo "Installing python requirements with pip..."
pip install -r ../requirements.txt
