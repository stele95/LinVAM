 #!/bin/bash
version=$(<../VERSION)
dir="linvam-v$version"
mkdir $dir
sh ./build.sh
cp ../build/linvam $dir
cp ../build/linvamconsole $dir
cp setup.sh $dir
cp setup-and-install.sh $dir
cp ../src/LinVAM.desktop $dir
cp configure-ydotoold.sh $dir
cp -r ../src/model $dir
zip -r "$dir.zip" $dir
rm -r $dir
