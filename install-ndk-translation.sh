#!/usr/bin/env bash
this_file="install-ndk-translation"

dir=$(pwd)
echo $dir
file=$(find $dir -name $this_file.sh)
dirname="${file%/*}"
cd $dirname
python waydroid_extras.py --$this_file