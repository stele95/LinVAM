#!/bin/bash
linvam=$(ps --no-headers -C linvam -o args,state)
linvamrun=$(ps --no-headers -C linvamrun -o args,state)
if [ -n "$linvam" ] || [ -n "$linvamrun" ]
    then
        cat ~/.local/share/LinVAM/config | jq '.profile' | sed "s/\"//g"
    else
        echo "OFF"
fi
