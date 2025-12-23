#!/usr/bin/env bash

if pgrep -x mpv > /dev/null; then
    pkill mpv
else
    runbg mpv --no-video https://www.youtube.com/live/jfKfPfyJRdk?si=OF0HKrYFFj33BzMo
fi
