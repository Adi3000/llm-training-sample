#!/bin/bash

WIN_FFXIV_DATA="D:\\Program Files\\SquareEnix\\FINAL FANTASY XIV - A Realm Reborn"
WSL_SAINTCOINACH_HOME="/mnt/g/Utils/SaintCoinach"
LANGUAGE="French"
cd "$WSL_SAINTCOINACH_HOME"
"/mnt/g/Utils/SaintCoinach/SaintCoinach.Cmd.exe" "$WIN_FFXIV_DATA" "exdheader"

cat 202*/exd-header.json | jq .[].Name | grep "quest/" | sed -e s/\"//g | xargs -P8 -I {} bash -c 'yes n | ./SaintCoinach.Cmd.exe "D:\Program Files\SquareEnix\FINAL FANTASY XIV - A Realm Reborn" "lang $LANGUAGE" "exd {}"'

cd -
