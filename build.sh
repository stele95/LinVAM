#!/bin/bash
python3 -m nuitka \
    --output-dir=build \
    --output-filename=linvam \
    --follow-import-to=commandeditwnd \
    --follow-import-to=keyactioneditwnd \
    --follow-import-to=mouseactioneditwnd \
    --follow-import-to=pauseactioneditwnd \
    --follow-import-to=profileeditwnd \
    --follow-import-to=profileexecutor \
    --follow-import-to=soundactioneditwnd \
    --follow-import-to=soundfiles \
    --follow-import-to=ui_commandeditwnd \
    --follow-import-to=ui_keyactioneditwnd \
    --follow-import-to=ui_mainwnd \
    --follow-import-to=ui_mouseactioneditwnd \
    --follow-import-to=ui_pauseactioneditwnd \
    --follow-import-to=ui_profileeditwnd \
    --follow-import-to=ui_soundactioneditwnd \
    linvam.py
