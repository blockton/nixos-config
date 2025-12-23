#!/usr/bin/env bash

wallpaper_path=$HOME/Pictures/wallpapers
wallpapers_folder=$HOME/Pictures/wallpapers/others
wallpaper_name="$(find "$wallpapers_folder" -maxdepth 1 -type f -printf "%f\n" | rofi -dmenu || pkill rofi)"

if [[ -f $wallpapers_folder/$wallpaper_name ]]; then
    ln -sf "$wallpapers_folder/$wallpaper_name" "$wallpaper_path/wallpaper"
    wall-change "$wallpaper_path/wallpaper"
else
    exit 1
fi
