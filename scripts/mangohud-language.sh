#!/bin/bash
linvam=$(ps --no-headers -C linvam -o args,state)
linvamrun=$(ps --no-headers -C linvamrun -o args,state)
if [ -n "$linvamrun" ] || [ -f ~/.local/share/LinVAM/.linvamrun ]
then
  if [ -f ~/.local/share/LinVAM/.linvamrun ]
  then
    cat ~/.local/share/LinVAM/.linvamrun | jq '.language' | sed "s/\"//g"
  fi
elif [ -n "$linvam" ] || [ -f ~/.local/share/LinVAM/.linvam ]
then
  if [ -f ~/.local/share/LinVAM/.linvam ]
    then
      cat ~/.local/share/LinVAM/.linvam | jq '.language' | sed "s/\"//g"
  fi
fi
