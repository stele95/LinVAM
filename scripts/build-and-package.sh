#!/bin/bash
version=$(<../VERSION)
dir="linvam-v$version"
mkdir $dir
sh ./build.sh
cp linvam $dir
cp linvamrun $dir
cp setup-and-install.sh $dir
cp mangohud-profile.sh $dir
cp mangohud-language.sh $dir
cp setup-mangohud.sh $dir
cp ../src/LinVAM.desktop $dir
cp ../requirements.txt $dir
cp configure-ydotoold.sh $dir
zip -r "$dir.zip" $dir
rm -r $dir
