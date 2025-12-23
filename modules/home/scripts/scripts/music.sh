#!/usr/bin/env bash

if pgrep -x audacious > /dev/null; then
    pkill audacious
else
    hyprctl dispatch exec "[workspace 5 silent] audacious -t ~/Music/playlist"
    sleep 0.5
    audtool playlist-repeat-status | grep "on" || audtool playlist-repeat-toggle
    audtool playlist-shuffle-status | grep "on" || audtool playlist-shuffle-toggle
fi
