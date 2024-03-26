 #!/bin/bash
version=$(<VERSION)
dir="linvam-v$version"
mkdir $dir
sh ./build.sh
cp build/linvam $dir
cp build/linvamconsole $dir
cp setup.sh $dir
cp setup-and-install.sh $dir
cp LinVAM.desktop $dir
cp -r model $dir
zip -r "$dir.zip" $dir
rm -r $dir
