#!/bin/bash
linvam=$(ps --no-headers -C linvam -o args,state)
linvamrun=$(ps --no-headers -C linvamrun -o args,state)
if [ -n "$linvamrun" ] || [ -f ~/.local/share/LinVAM/.linvamrun ]
then
  if [ -f ~/.local/share/LinVAM/.linvamrun ]
  then
    language=$(cat ~/.local/share/LinVAM/.linvamrun | grep "language" | sed "s/\"language\"://g;s/^[ \t]*//;s/[\",]//g;s/[ \t]*$//")
    echo "$language"
  else
    echo "ON"
  fi
elif [ -n "$linvam" ] || [ -f ~/.local/share/LinVAM/.linvam ]
then
  if [ -f ~/.local/share/LinVAM/.linvam ]
    then
      language=$(cat ~/.local/share/LinVAM/.linvam | grep "language" | sed "s/\"language\"://g;s/^[ \t]*//;s/[\",]//g;s/[ \t]*$//")
      echo "$language"
    else
      echo "ON"
  fi
else
  echo "OFF"
fi
