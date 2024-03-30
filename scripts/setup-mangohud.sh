if [ -f ~/.config/MangoHud/MangoHud.conf ]
  then
      cp mangohud-profile.sh ~/.local/share/LinVAM/
      cp mangohud-language.sh ~/.local/share/LinVAM/
      {
        echo "custom_text=LinVAM";
        echo "exec=~/.local/share/LinVAM//mangohud-profile.sh";
        echo "exec=~/.local/share/LinVAM/mangohud-language.sh";
      } >> ~/.config/MangoHud/MangoHud.conf
  else
      echo "MangoHud.conf file not found in ~/.config/MangoHud/"
fi