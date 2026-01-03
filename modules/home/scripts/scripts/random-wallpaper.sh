#!/usr/bin/env bash
mkdir -p ~/Pictures/wallpapers/others
if cp -r wallpapers/otherWallpaper/*/* ~/Pictures/wallpapers/others/ &&
    ln -sf "$PWD/wallpapers/wallpaper.png" ~/Pictures/wallpapers/wallpaper; then
else
    echo -e "${WARN}Some wallpapers could not be copied!"
fi

wallpaper_path="$HOME/Pictures/wallpapers"
wallpapers_folder="$HOME/Pictures/wallpapers/others"

current_wallpaper=$(readlink "$wallpaper_path/wallpaper" 2> /dev/null)
current_wallpaper_name="$(basename "$current_wallpaper")"

mapfile -t wallpaper_list < <(ls "$wallpapers_folder")
wallpaper_count=${#wallpaper_list[@]}

while true; do
    wallpaper_name="${wallpaper_list[RANDOM % wallpaper_count]}"

    if [[ "$wallpaper_name" != "$current_wallpaper_name" ]]; then
        break
    fi
done

ln -sf "$wallpapers_folder/$wallpaper_name" "$wallpaper_path/wallpaper"
wall-change "$wallpaper_path/wallpaper" &
