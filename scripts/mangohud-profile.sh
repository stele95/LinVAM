#!/bin/bash
linvam=$(ps --no-headers -C linvam -o args,state)
linvamrun=$(ps --no-headers -C linvamrun -o args,state)
if [ -n "$linvamrun" ] || [ -f ~/.local/share/LinVAM/.linvamrun ]
then
  if [ -f ~/.local/share/LinVAM/.linvamrun ]
  then
    profile=$(cat ~/.local/share/LinVAM/.linvamrun | grep "profile" | sed "s/\"profile\"://g;s/^[ \t]*//;s/[\",]//g;s/[ \t]*$//")
    echo "$profile"
  else
    echo "ON"
  fi
elif [ -n "$linvam" ] || [ -f ~/.local/share/LinVAM/.linvam ]
then
  if [ -f ~/.local/share/LinVAM/.linvam ]
    then
      profile=$(cat ~/.local/share/LinVAM/.linvam | grep "profile" | sed "s/\"profile\"://g;s/^[ \t]*//;s/[\",]//g;s/[ \t]*$//")
      echo "$profile"
    else
      echo "ON"
  fi
else
  echo "OFF"
fi
