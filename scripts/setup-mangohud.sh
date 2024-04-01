if [ -f ~/.config/MangoHud/MangoHud.conf ]
  then
    mangohud_linvam=$(cat ~/.config/MangoHud/MangoHud.conf | grep 'custom_text=LinVAM')
    if [ -n "$mangohud_linvam" ]
    then
      echo "Already set up, skipping..."
    else
      cp mangohud-profile.sh ~/.local/share/LinVAM/
      cp mangohud-language.sh ~/.local/share/LinVAM/
      {
        echo "custom_text=LinVAM";
        echo "exec=sh ~/.local/share/LinVAM/mangohud-profile.sh";
        echo "exec=sh ~/.local/share/LinVAM/mangohud-language.sh";
      } >> ~/.config/MangoHud/MangoHud.conf
    fi
  else
      echo "MangoHud.conf file not found in ~/.config/MangoHud/"
fi